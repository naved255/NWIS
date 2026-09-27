from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from .features import engineer_features, infer_feature_columns
from .metrics import evaluate_binary, tune_threshold
from .models import build_model
from .preprocessing import build_preprocessor
from .schemas import RiskPrediction, TrainingConfig
from .splitting import temporal_split

logger = logging.getLogger(__name__)

class RiskPredictionEngine:
    """Train, persist, and serve a binary drilling-risk model for one risk type."""

    def __init__(self, artifact_dir: Optional[str] = None, model_version: Optional[str] = None):
        self.artifact_dir = Path(artifact_dir or os.getenv("NWIS_RISK_ARTIFACT_DIR", "artifacts/risk_engine"))
        self.model_version = model_version or os.getenv("NWIS_RISK_MODEL_VERSION", "1.0.0")
        self.pipeline: Optional[Pipeline] = None
        self.feature_columns = []
        self.threshold = 0.5
        self.risk_type = None
        self.metadata: Dict[str, Any] = {}

    def fit(self, df: pd.DataFrame, risk_type: str, config: Optional[TrainingConfig] = None) -> Dict[str, Any]:
        """Train one binary risk model and return validation/test metrics."""
        cfg = config or TrainingConfig()
        self._validate_training_data(df, cfg)
        if cfg.target_column not in df.columns:
            raise ValueError(f"Missing target column: {cfg.target_column}")
        data = engineer_features(df)
        data = data.dropna(subset=[cfg.target_column]).copy()
        y = (data[cfg.target_column].astype(str) == str(risk_type)).astype(int)
        if y.nunique() < 2:
            raise ValueError("Training target must contain both positive and negative examples")
        feature_columns = infer_feature_columns(data, cfg.target_column, cfg.time_column, cfg.group_column)
        if not feature_columns:
            raise ValueError("No usable feature columns found")

        # Split BEFORE fitting preprocessing. Temporal ordering is preferred whenever timestamp exists.
        work = data[feature_columns + [cfg.target_column] + ([cfg.time_column] if cfg.time_column and cfg.time_column in data else [])].copy()
        work["__target__"] = y.values
        train, val, test = temporal_split(work, cfg.time_column, cfg.test_size, cfg.validation_size)
        y_train, y_val, y_test = train["__target__"], val["__target__"], test["__target__"]
        X_train, X_val, X_test = train[feature_columns], val[feature_columns], test[feature_columns]

        pos, neg = int(y_train.sum()), int((y_train == 0).sum())
        scale_pos_weight = (neg / pos) if cfg.use_class_weights and pos else 1.0
        preprocessor = build_preprocessor(X_train, feature_columns)
        model = build_model(cfg.model_type, cfg.random_state, cfg.n_estimators, cfg.learning_rate, cfg.max_depth, scale_pos_weight)
        pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])
        pipeline.fit(X_train, y_train)

        val_prob = pipeline.predict_proba(X_val)[:, 1]
        threshold = tune_threshold(y_val, val_prob, cfg.threshold_metric, cfg.target_recall)
        test_prob = pipeline.predict_proba(X_test)[:, 1]
        test_metrics = evaluate_binary(y_test, test_prob, threshold)
        val_metrics = evaluate_binary(y_val, val_prob, threshold)

        self.pipeline = pipeline
        self.feature_columns = feature_columns
        self.threshold = threshold
        self.risk_type = risk_type
        self.metadata = {
            "model_version": self.model_version,
            "risk_type": risk_type,
            "model_type": cfg.model_type,
            "target_column": cfg.target_column,
            "feature_columns": feature_columns,
            "threshold": threshold,
            "class_balance_train": {"positive": pos, "negative": neg},
            "validation": val_metrics,
            "test": test_metrics,
            "leakage_control": "chronological split when a valid timestamp is supplied; preprocessing fit on train only",
        }
        self.save()
        return self.metadata

    def predict_risk(self, features: Dict[str, Any] | pd.DataFrame) -> RiskPrediction:
        """Predict the configured risk for one observation or one-row DataFrame."""
        if self.pipeline is None:
            raise RuntimeError("Model is not loaded/trained")
        X = pd.DataFrame([features]) if isinstance(features, dict) else features.copy()
        X = engineer_features(X)
        for col in self.feature_columns:
            if col not in X.columns:
                X[col] = np.nan
        probability = float(self.pipeline.predict_proba(X[self.feature_columns])[:, 1][0])
        severity = self._severity(probability)
        # Confidence measures distance from the tuned decision boundary, not model certainty.
        confidence = float(min(1.0, abs(probability - self.threshold) / max(self.threshold, 1 - self.threshold, 1e-9) + 0.5))
        return RiskPrediction(risk_type=self.risk_type or "unknown", probability=probability,
                              severity=severity, confidence=confidence, model_version=self.model_version)

    def save(self) -> None:
        """Persist pipeline, metadata, and threshold in one artifact directory."""
        if self.pipeline is None:
            raise RuntimeError("Nothing to save")
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, self.artifact_dir / "model.joblib")
        (self.artifact_dir / "metadata.json").write_text(json.dumps(self.metadata, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, artifact_dir: str) -> "RiskPredictionEngine":
        """Load a previously saved complete preprocessing+model artifact."""
        path = Path(artifact_dir)
        meta = json.loads((path / "metadata.json").read_text(encoding="utf-8"))
        engine = cls(artifact_dir, meta["model_version"])
        engine.pipeline = joblib.load(path / "model.joblib")
        engine.feature_columns = meta["feature_columns"]
        engine.threshold = float(meta["threshold"])
        engine.risk_type = meta["risk_type"]
        engine.metadata = meta
        return engine

    @staticmethod
    def _validate_training_data(df: pd.DataFrame, cfg: TrainingConfig) -> None:
        """Validate basic training data invariants before model fitting."""
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("Training data must be a non-empty pandas DataFrame")
        if cfg.target_column not in df.columns:
            raise ValueError(f"Missing target column: {cfg.target_column}")
        if df[cfg.target_column].dropna().empty:
            raise ValueError("Training target contains no usable labels")
        if cfg.time_column and cfg.time_column in df.columns:
            parsed = pd.to_datetime(df[cfg.time_column], errors="coerce", utc=True)
            if parsed.isna().any():
                logger.warning("%d rows have invalid timestamps and may trigger the non-temporal split fallback", int(parsed.isna().sum()))
        if df.duplicated().any():
            logger.warning("Training data contains %d exact duplicate rows", int(df.duplicated().sum()))

    @staticmethod
    def _severity(probability: float) -> str:
        if probability >= 0.85: return "critical"
        if probability >= 0.65: return "high"
        if probability >= 0.40: return "medium"
        return "low"
