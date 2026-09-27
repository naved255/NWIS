from __future__ import annotations
from typing import Any


def build_model(model_type: str, random_state: int, n_estimators: int, learning_rate: float,
                max_depth: int, scale_pos_weight: float = 1.0) -> Any:
    """Construct the requested gradient boosting classifier."""
    if model_type == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(
            objective="binary", n_estimators=n_estimators, learning_rate=learning_rate,
            max_depth=max_depth, random_state=random_state, class_weight=None,
            scale_pos_weight=scale_pos_weight, n_jobs=-1, verbosity=-1,
        )
    if model_type == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(
            n_estimators=n_estimators, learning_rate=learning_rate, max_depth=max_depth,
            random_state=random_state, eval_metric="logloss", scale_pos_weight=scale_pos_weight,
            n_jobs=-1, tree_method="hist",
        )
    if model_type == "hist_gradient_boosting":
        from sklearn.ensemble import HistGradientBoostingClassifier
        return HistGradientBoostingClassifier(
            max_iter=n_estimators, learning_rate=learning_rate, max_depth=max_depth,
            random_state=random_state, class_weight="balanced" if scale_pos_weight != 1 else None,
        )
    raise ValueError(f"Unsupported model_type: {model_type}")
