"""Pydantic v2 schemas exposed by the storage layer."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class WellCreate(BaseModel):
    well_id: str = Field(min_length=1, max_length=100)
    well_name: str | None = None
    field_name: str | None = None
    block_name: str | None = None
    operator: str | None = None
    status: str | None = None
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)
    total_depth_m: Decimal | None = Field(default=None, ge=0)
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class WellRead(ORMModel):
    id: str
    well_id: str
    well_name: str | None
    field_name: str | None
    block_name: str | None
    operator: str | None
    status: str | None
    latitude: Decimal
    longitude: Decimal
    total_depth_m: Decimal | None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class TrajectoryPointCreate(BaseModel):
    measured_depth_m: Decimal = Field(ge=0)
    inclination_deg: Decimal | None = None
    azimuth_deg: Decimal | None = None
    tvd_m: Decimal | None = Field(default=None, ge=0)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    sequence_no: int = Field(ge=0)
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class DrillingParameterRead(ORMModel):
    id: str
    well_id: str
    recorded_at: datetime
    measured_depth_m: Decimal | None
    weight_on_bit_kn: Decimal | None
    rotary_rpm: Decimal | None
    torque_kn_m: Decimal | None
    rate_of_penetration_m_hr: Decimal | None
    standpipe_pressure_kpa: Decimal | None
    flow_rate_lpm: Decimal | None
    mud_weight_kg_m3: Decimal | None
    mud_viscosity_cp: Decimal | None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class FormationRead(ORMModel):
    id: str
    well_id: str
    formation_name: str
    top_depth_m: Decimal | None
    base_depth_m: Decimal | None
    lithology: str | None
    age: str | None
    stratigraphic_group: str | None
    properties: dict[str, Any] | None = None


class GeologicalInformationRead(ORMModel):
    id: str
    well_id: str
    depth_from_m: Decimal | None
    depth_to_m: Decimal | None
    lithology: str | None
    porosity_pct: Decimal | None
    permeability_md: Decimal | None
    pressure_kpa: Decimal | None
    temperature_c: Decimal | None
    properties: dict[str, Any] | None = None


class DrillingEventRead(ORMModel):
    id: str
    well_id: str
    event_type: str
    event_time: datetime
    depth_m: Decimal | None
    severity: str | None
    description: str | None
    duration_min: Decimal | None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class DocumentRead(ORMModel):
    id: str
    document_id: str
    well_id: str | None
    document_type: str
    title: str | None
    storage_key: str
    mime_type: str | None
    checksum_sha256: str | None
    page_count: int | None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class DocumentChunkRead(ORMModel):
    id: str
    document_id: str
    chunk_index: int
    text: str
    page_number: int | None
    formation: str | None
    depth_from_m: Decimal | None
    depth_to_m: Decimal | None
    event_type: str | None
    qdrant_point_id: str | None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class PredictionRead(ORMModel):
    id: str
    well_id: str
    model_version_id: str | None
    prediction_type: str
    predicted_value: Decimal | None
    risk_score: Decimal | None
    severity: str | None
    predicted_at: datetime
    explanation: dict[str, Any] | None
    input_snapshot: dict[str, Any] | None


class AlertRead(ORMModel):
    id: str
    well_id: str | None
    prediction_id: str | None
    alert_type: str
    severity: str
    status: str
    message: str
    triggered_at: datetime
    acknowledged_at: datetime | None


class RecommendationRead(ORMModel):
    id: str
    well_id: str | None
    prediction_id: str | None
    recommendation_type: str
    priority: str | None
    title: str
    description: str
    rationale: str | None
    status: str


class ModelVersionRead(ORMModel):
    id: str
    model_name: str
    version: str
    artifact_uri: str | None
    metrics: dict[str, Any] | None
    feature_schema: dict[str, Any] | None
    is_active: bool


class UserRead(ORMModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool


class SimilarWellMetadata(WellRead):
    distance_km: float
    formation_matches: list[str] = []
    event_types: list[str] = []


class QdrantChunkPayload(BaseModel):
    chunk_id: str
    document_id: str
    well_id: str | None = None
    formation: str | None = None
    depth: float | None = None
    depth_from_m: float | None = None
    depth_to_m: float | None = None
    document_type: str | None = None
    event_type: str | None = None
    page_number: int | None = None
    text: str
    metadata: dict[str, Any] = {}


class ObjectMetadata(BaseModel):
    key: str
    content_type: str | None = None
    size_bytes: int | None = None
    etag: str | None = None


RiskSeverity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
