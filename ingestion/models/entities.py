"""Canonical NWIS ingestion entities."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class SourceMetadata(BaseModel):
    """Metadata identifying where and when an ingested record originated."""
    model_config = ConfigDict(extra="allow")

    source_type: Literal["csv", "json", "pdf", "api", "database", "sample"]
    source_name: str
    source_uri: str | None = None
    source_record_id: str | None = None
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: str = "1.0"


class NWISEntity(BaseModel):
    """Base class shared by all standardized NWIS entities."""
    model_config = ConfigDict(extra="ignore")

    source_metadata: SourceMetadata


class Well(NWISEntity):
    """Canonical well/master-data record."""
    well_id: str = Field(min_length=1)
    well_name: str | None = None
    field_name: str | None = None
    block: str | None = None
    basin: str | None = None
    operator: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    spud_date: date | None = None
    completion_date: date | None = None
    status: str | None = None
    total_depth: float | None = Field(default=None, ge=0)


class DrillingParameter(NWISEntity):
    """Canonical drilling/mud parameter observation."""
    well_id: str = Field(min_length=1)
    observed_at: datetime | None = None
    depth: float | None = Field(default=None, ge=0)
    rop: float | None = Field(default=None, ge=0)
    wob: float | None = Field(default=None, ge=0)
    rpm: float | None = Field(default=None, ge=0)
    torque: float | None = Field(default=None, ge=0)
    hookload: float | None = Field(default=None, ge=0)
    mud_weight: float | None = Field(default=None, ge=0)
    mud_flow_rate: float | None = Field(default=None, ge=0)
    standpipe_pressure: float | None = Field(default=None, ge=0)
    pump_pressure: float | None = Field(default=None, ge=0)
    temperature: float | None = None
    bit_size: float | None = Field(default=None, ge=0)
    bit_type: str | None = None


class DrillingEvent(NWISEntity):
    """Canonical operational/drilling event."""
    event_id: str | None = None
    well_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    occurred_at: datetime | None = None
    depth: float | None = Field(default=None, ge=0)
    severity: str | None = None
    description: str | None = None
    duration_minutes: float | None = Field(default=None, ge=0)
    attributes: dict[str, Any] = Field(default_factory=dict)


class TrajectoryPoint(NWISEntity):
    """Canonical directional survey/trajectory point."""
    well_id: str = Field(min_length=1)
    measured_depth: float = Field(ge=0)
    inclination: float = Field(ge=0, le=180)
    azimuth: float = Field(ge=0, le=360)
    true_vertical_depth: float | None = Field(default=None, ge=0)
    northing: float | None = None
    easting: float | None = None
    dogleg_severity: float | None = Field(default=None, ge=0)
    surveyed_at: datetime | None = None


class DocumentMetadata(NWISEntity):
    """Metadata for source documents; extraction/OCR is intentionally out of scope."""
    document_id: str = Field(min_length=1)
    document_type: str = Field(min_length=1)
    file_name: str = Field(min_length=1)
    mime_type: str | None = None
    file_size_bytes: int | None = Field(default=None, ge=0)
    well_id: str | None = None
    document_date: date | None = None
    checksum_sha256: str | None = None
    page_count: int | None = Field(default=None, ge=0)
    extraction_status: str = "not_extracted"


ENTITY_MODELS: dict[str, type[NWISEntity]] = {
    "well": Well,
    "drilling_parameter": DrillingParameter,
    "drilling_event": DrillingEvent,
    "trajectory_point": TrajectoryPoint,
    "document_metadata": DocumentMetadata,
}
