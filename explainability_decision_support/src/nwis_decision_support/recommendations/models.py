from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

class EvidenceItem(BaseModel):
    """Evidence supplied by an existing NWIS source."""
    source_id: str
    source_type: Literal["historical_well", "historical_event", "document", "prediction", "alert"]
    well_id: str | None = None
    event_type: str | None = None
    similarity: float | None = Field(default=None, ge=0, le=1)
    depth_m: float | None = None
    formation: str | None = None
    title: str | None = None
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class RecommendationContext(BaseModel):
    """Inputs for evidence-backed recommendation generation."""
    well_id: str
    risk_type: str
    probability: float = Field(ge=0, le=1)
    severity: str
    depth_m: float | None = None
    formation: str | None = None
    prediction_id: str | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    alert_reason: str | None = None

class RecommendationResult(BaseModel):
    """Recommendation with explicit evidence sufficiency."""
    recommendation_id: str
    well_id: str
    risk_type: str
    priority: str
    title: str
    recommendation: str
    rationale: str
    evidence_sufficient: bool
    evidence: list[EvidenceItem]
    disclaimer: str
