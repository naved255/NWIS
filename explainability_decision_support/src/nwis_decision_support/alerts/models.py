from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high", "critical"]

class HistoricalEvidence(BaseModel):
    """Historical incident evidence supplied by RAG/geospatial services."""
    well_id: str
    event_type: str
    similarity: float = Field(ge=0, le=1)
    depth_start_m: float | None = None
    depth_end_m: float | None = None
    formation: str | None = None
    source_id: str | None = None
    source_type: str = "historical_event"
    summary: str | None = None

class ParameterAnomaly(BaseModel):
    """Realtime anomaly supplied by the realtime/ML layer."""
    parameter: str
    value: Any
    baseline: Any | None = None
    anomaly_score: float | None = None
    is_anomalous: bool = True

class AlertContext(BaseModel):
    """Inputs required to evaluate configurable NWIS alert rules."""
    well_id: str
    risk_type: str
    probability: float = Field(ge=0, le=1)
    severity: Severity
    depth_m: float | None = None
    formation: str | None = None
    risk_interval_start_m: float | None = None
    risk_interval_end_m: float | None = None
    historical_evidence: list[HistoricalEvidence] = Field(default_factory=list)
    parameter_anomalies: list[ParameterAnomaly] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recommended_action: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class AlertRule(BaseModel):
    """Configurable rule used by the alert engine."""
    name: str
    enabled: bool = True
    min_probability: float | None = Field(default=None, ge=0, le=1)
    severities: set[Severity] | None = None
    min_historical_similarity: float | None = Field(default=None, ge=0, le=1)
    require_historical_match: bool = False
    require_depth_in_interval: bool = False
    depth_tolerance_m: float = Field(default=50, ge=0)
    require_parameter_anomaly: bool = False
    formation: str | None = None
    output_severity: Severity = "high"

class AlertResult(BaseModel):
    """Generated alert; `None` means no rule fired."""
    alert_id: str | None = None
    generated: bool
    well_id: str
    risk_type: str
    severity: Severity | None = None
    probability: float
    depth_m: float | None = None
    reason: str | None = None
    evidence: list[HistoricalEvidence] = Field(default_factory=list)
    timestamp: datetime
    recommended_action: str | None = None
    rule_name: str | None = None
