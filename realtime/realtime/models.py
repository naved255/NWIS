from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DrillingParameterUpdate(BaseModel):
    """Canonical drilling-parameter payload used between adapters and NWIS."""

    model_config = ConfigDict(extra="allow")

    well_id: str = Field(min_length=1, max_length=128)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    depth: float = Field(ge=0)
    rop: float = Field(ge=0)
    wob: float = Field(ge=0)
    rpm: float = Field(ge=0)
    torque: float = Field(ge=0)
    pressure: float = Field(ge=0)
    mud_flow: float = Field(ge=0)
    mud_weight: float = Field(ge=0)
    source: str = "ertmac"
    sequence: int | None = Field(default=None, ge=0)

    @field_validator("timestamp")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class ValidationIssue(BaseModel):
    """Validation issue detected in an incoming real-time sample."""

    field: str
    code: str
    message: str
    value: Any = None
    severity: Literal["warning", "error"] = "error"


class NormalizedRealtimeEvent(BaseModel):
    """Event emitted by the real-time pipeline after validation/normalization."""

    event_type: Literal["parameter_update", "abnormal_parameter", "stream_status"]
    well_id: str
    timestamp: datetime
    parameters: DrillingParameterUpdate | None = None
    abnormal_fields: list[str] = Field(default_factory=list)
    issues: list[ValidationIssue] = Field(default_factory=list)
    source: str = "ertmac"
    stream_status: str | None = None


class StreamCommand(BaseModel):
    """Control command sent by a WebSocket client."""

    action: Literal["start", "stop", "ping"]


class StreamStatus(BaseModel):
    """Current state of a well stream."""

    well_id: str
    running: bool
    adapter: str
    message: str
