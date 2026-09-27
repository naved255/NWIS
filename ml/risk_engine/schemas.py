from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

RiskType = Literal[
    "mud_loss", "stuck_pipe", "kick", "torque_spike", "overpressure",
    "cementing_issue", "npt", "drilling_anomaly"
]

class RiskPrediction(BaseModel):
    risk_type: str
    probability: float = Field(ge=0.0, le=1.0)
    severity: Literal["low", "medium", "high", "critical"]
    confidence: float = Field(ge=0.0, le=1.0)
    model_version: str

class TrainingConfig(BaseModel):
    model_type: Literal["lightgbm", "xgboost", "hist_gradient_boosting"] = "lightgbm"
    target_column: str = "risk_type"
    positive_label: Optional[str] = None
    time_column: Optional[str] = "timestamp"
    group_column: Optional[str] = "well_id"
    test_size: float = Field(default=0.2, gt=0, lt=0.5)
    validation_size: float = Field(default=0.2, gt=0, lt=0.5)
    random_state: int = 42
    target_recall: float = Field(default=0.80, gt=0, lt=1)
    threshold_metric: Literal["f1", "recall"] = "f1"
    use_class_weights: bool = True
    max_resample_ratio: float = Field(default=0.50, gt=0, le=1)
    n_estimators: int = 300
    learning_rate: float = 0.05
    max_depth: int = 7

class EvaluationResult(BaseModel):
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float]
    pr_auc: Optional[float]
    confusion_matrix: List[List[int]]
    threshold: float
    support: int
