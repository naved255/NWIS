from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Literal

Direction = Literal["increases_risk", "decreases_risk", "neutral"]

class FeatureContribution(BaseModel):
    """One model feature and its SHAP contribution."""
    feature: str
    value: Any
    contribution: float
    direction: Direction

class ExplanationResult(BaseModel):
    """Human-readable and machine-readable explanation of one prediction."""
    prediction_id: str | None = None
    well_id: str | None = None
    risk_type: str
    probability: float | None = Field(default=None, ge=0, le=1)
    base_value: float | None = None
    predicted_value: float | None = None
    features: list[FeatureContribution]
    explanation: str
    method: str = "shap"
