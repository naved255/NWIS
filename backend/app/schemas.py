from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Pagination(BaseModel):
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class WellResponse(APIModel):
    id: str
    well_id: str
    well_name: str | None = None
    field_name: str | None = None
    block_name: str | None = None
    operator: str | None = None
    status: str | None = None
    latitude: Decimal
    longitude: Decimal
    total_depth_m: Decimal | None = None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class WellListResponse(BaseModel):
    items: list[WellResponse]
    pagination: Pagination


class NearbyWellResponse(WellResponse):
    distance_km: float
    formation_matches: list[str] = Field(default_factory=list)
    event_types: list[str] = Field(default_factory=list)


class NearbyWellsResponse(BaseModel):
    source_well_id: str
    radius_km: float
    items: list[NearbyWellResponse]
    pagination: Pagination


class DrillingEventResponse(APIModel):
    id: str
    well_id: str
    event_type: str
    event_time: datetime
    depth_m: Decimal | None = None
    severity: str | None = None
    description: str | None = None
    duration_min: Decimal | None = None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class EventListResponse(BaseModel):
    items: list[DrillingEventResponse]
    pagination: Pagination


class TrajectoryPointResponse(APIModel):
    id: str
    well_id: str
    measured_depth_m: Decimal
    inclination_deg: Decimal | None = None
    azimuth_deg: Decimal | None = None
    tvd_m: Decimal | None = None
    northing_m: Decimal | None = None
    easting_m: Decimal | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    sequence_no: int
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class TrajectoryResponse(BaseModel):
    well_id: str
    items: list[TrajectoryPointResponse]


class MonitoringSnapshotResponse(BaseModel):
    well_id: str
    timestamp: datetime | None = None
    depth: float | None = None
    rop: float | None = None
    wob: float | None = None
    rpm: float | None = None
    torque: float | None = None
    pressure: float | None = None
    mud_flow: float | None = None
    mud_weight: float | None = None
    formation: str | None = None


class TrendPointResponse(BaseModel):
    timestamp: datetime
    depth: float | None = None
    rop: float | None = None
    torque: float | None = None
    pressure: float | None = None


class DocumentResponse(APIModel):
    id: str
    document_id: str
    well_id: str | None = None
    document_type: str
    title: str | None = None
    storage_key: str
    mime_type: str | None = None
    checksum_sha256: str | None = None
    page_count: int | None = None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias=AliasChoices("metadata", "metadata_json"))


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    pagination: Pagination


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    well_id: str | None = None
    document_type: str | None = None
    event_type: str | None = None
    formation: str | None = None
    limit: int = Field(default=10, ge=1, le=100)


class SearchResult(BaseModel):
    result_id: str
    score: float | None = None
    title: str | None = None
    text: str
    source_uri: str | None = None
    document_id: str | None = None
    well_id: str | None = None
    page: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    items: list[SearchResult]


class RAGRequest(SearchRequest):
    include_sources: bool = True


class RAGResponse(BaseModel):
    question: str
    answer: str
    sources: list[SearchResult] = Field(default_factory=list)


class RiskPredictionRequest(BaseModel):
    well_id: str | None = None
    risk_type: str | None = None
    features: dict[str, Any] = Field(default_factory=dict)


class RiskPredictionResponse(BaseModel):
    prediction_id: str
    well_id: str | None = None
    risk_type: str
    probability: float = Field(ge=0, le=1)
    severity: Literal["low", "medium", "high", "critical"]
    confidence: float = Field(ge=0, le=1)
    model_version: str
    explanation: dict[str, Any] | None = None
    predicted_at: datetime


class PredictionListResponse(BaseModel):
    items: list[RiskPredictionResponse]
    pagination: Pagination


class AlertResponse(BaseModel):
    id: str
    well_id: str | None = None
    prediction_id: str | None = None
    alert_type: str
    severity: str
    status: str
    message: str
    triggered_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    pagination: Pagination


class RecommendationResponse(BaseModel):
    id: str
    well_id: str | None = None
    prediction_id: str | None = None
    recommendation_type: str
    priority: str | None = None
    title: str
    description: str
    rationale: str | None = None
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecommendationListResponse(BaseModel):
    items: list[RecommendationResponse]
    pagination: Pagination


class RealtimeStatusResponse(BaseModel):
    status: Literal["connected", "degraded", "offline"]
    source: str
    last_event_at: datetime | None = None
    message: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str
    version: str
    dependencies: dict[str, str]
