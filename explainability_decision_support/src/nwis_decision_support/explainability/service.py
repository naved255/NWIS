from __future__ import annotations
from typing import Any, Mapping
import math

from .models import ExplanationResult, FeatureContribution


def _direction(contribution: float) -> str:
    if contribution > 1e-12:
        return "increases_risk"
    if contribution < -1e-12:
        return "decreases_risk"
    return "neutral"


def _load_shap():
    try:
        import shap
        return shap
    except ImportError as exc:
        raise RuntimeError(
            "SHAP is required for explain_prediction(). Install the optional dependency with `pip install shap`."
        ) from exc


def _extract_shap_values(explainer: Any, row: Any):
    values = explainer(row)
    shap_values = values.values
    base_values = values.base_values
    # Binary classifiers can return [1, n_features] or [1, n_features, 2].
    if getattr(shap_values, "ndim", 0) == 3:
        shap_values = shap_values[0, :, -1]
    elif getattr(shap_values, "ndim", 0) == 2:
        shap_values = shap_values[0]
    else:
        shap_values = shap_values.reshape(-1)
    if getattr(base_values, "ndim", 0) == 2:
        base = float(base_values[0, -1])
    elif getattr(base_values, "ndim", 0) == 1:
        base = float(base_values[-1])
    else:
        base = float(base_values)
    return shap_values, base


def _human_explanation(items: list[FeatureContribution], probability: float | None) -> str:
    positive = [x for x in items if x.contribution > 0]
    negative = [x for x in items if x.contribution < 0]
    positive.sort(key=lambda x: abs(x.contribution), reverse=True)
    negative.sort(key=lambda x: abs(x.contribution), reverse=True)
    if not positive:
        if negative:
            names = ", ".join(x.feature.replace("_", " ") for x in negative[:2])
            return f"Risk was reduced mainly by {names} relative to the model baseline."
        return "The model explanation shows no material directional feature contribution."
    names = " and ".join(x.feature.replace("_", " ") for x in positive[:2])
    if probability is not None:
        return f"Risk increased mainly because {names} contributed positively to the prediction; the model probability is {probability:.0%}."
    return f"Risk increased mainly because {names} contributed positively to the prediction."


def explain_prediction(
    model: Any,
    features: Mapping[str, Any],
    risk_type: str,
    *,
    probability: float | None = None,
    prediction_id: str | None = None,
    well_id: str | None = None,
    top_k: int = 10,
) -> ExplanationResult:
    """Explain one prediction using SHAP for a tree-based model.

    `features` must contain the same model input feature names and values used by
    the trained model. The function does not alter model features or invent data.
    """
    if not features:
        raise ValueError("features must not be empty")
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    shap = _load_shap()
    import pandas as pd

    frame = pd.DataFrame([dict(features)])

    # The NWIS risk engine persists a sklearn Pipeline containing the
    # preprocessor and the tree model. TreeExplainer cannot consume the
    # Pipeline object directly, so explain the exact transformed row/model
    # pair used for inference. Plain tree models remain supported as before.
    explainer_model = model
    explain_frame = frame
    feature_names = list(frame.columns)
    display_values = [features[name] for name in feature_names]
    if hasattr(model, "named_steps") and "model" in model.named_steps and "preprocessor" in model.named_steps:
        preprocessor = model.named_steps["preprocessor"]
        explainer_model = model.named_steps["model"]
        explain_frame = preprocessor.transform(frame)
        try:
            feature_names = list(preprocessor.get_feature_names_out())
        except Exception:
            feature_names = [f"feature_{i}" for i in range(explain_frame.shape[1])]
        display_values = []
        for name in feature_names:
            raw_name = name.split("__", 1)[-1]
            display_values.append(features.get(raw_name, features.get(name)))

    explainer = shap.TreeExplainer(explainer_model)
    shap_values, base_value = _extract_shap_values(explainer, explain_frame)
    raw = [
        FeatureContribution(
            feature=name,
            value=display_values[i],
            contribution=float(shap_values[i]),
            direction=_direction(float(shap_values[i])),
        )
        for i, name in enumerate(feature_names)
        if i < len(shap_values) and math.isfinite(float(shap_values[i]))
    ]
    raw.sort(key=lambda x: abs(x.contribution), reverse=True)
    selected = raw[:top_k]

    predicted_value = None
    try:
        predicted_value = float(explainer.expected_value)
    except (TypeError, ValueError):
        predicted_value = base_value

    return ExplanationResult(
        prediction_id=prediction_id,
        well_id=well_id,
        risk_type=risk_type,
        probability=probability,
        base_value=base_value,
        predicted_value=predicted_value,
        features=selected,
        explanation=_human_explanation(selected, probability),
    )
