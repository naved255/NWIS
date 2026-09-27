"""SQLAlchemy/PostGIS models for NWIS persistent storage."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


def uuid_str() -> str:
    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Well(Base, TimestampMixin):
    __tablename__ = "wells"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    well_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    well_name: Mapped[str | None] = mapped_column(String(255))
    field_name: Mapped[str | None] = mapped_column(String(255), index=True)
    block_name: Mapped[str | None] = mapped_column(String(255))
    operator: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str | None] = mapped_column(String(50))
    spud_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completion_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    surface_location: Mapped[Any] = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=False)
    total_depth_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)

    trajectories: Mapped[list[WellTrajectory]] = relationship(back_populates="well", cascade="all, delete-orphan")
    parameters: Mapped[list[DrillingParameter]] = relationship(back_populates="well", cascade="all, delete-orphan")
    formations: Mapped[list[Formation]] = relationship(back_populates="well", cascade="all, delete-orphan")
    events: Mapped[list[DrillingEvent]] = relationship(back_populates="well", cascade="all, delete-orphan")
    documents: Mapped[list[Document]] = relationship(back_populates="well", cascade="all, delete-orphan")
    predictions: Mapped[list[Prediction]] = relationship(back_populates="well", cascade="all, delete-orphan")
    alerts: Mapped[list[Alert]] = relationship(back_populates="well", cascade="all, delete-orphan")
    recommendations: Mapped[list[Recommendation]] = relationship(back_populates="well", cascade="all, delete-orphan")
    geological_information: Mapped[list[GeologicalInformation]] = relationship(back_populates="well", cascade="all, delete-orphan")



class WellTrajectory(Base):
    __tablename__ = "well_trajectories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    measured_depth_m: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    inclination_deg: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    azimuth_deg: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    tvd_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    northing_m: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    easting_m: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    point: Mapped[Any | None] = mapped_column(Geometry("POINTZ", srid=4326, spatial_index=True))
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)

    well: Mapped[Well] = relationship(back_populates="trajectories")
    __table_args__ = (UniqueConstraint("well_id", "sequence_no", name="uq_trajectory_sequence"), Index("ix_trajectory_well_depth", "well_id", "measured_depth_m"))


class DrillingParameter(Base):
    __tablename__ = "drilling_parameters"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    measured_depth_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), index=True)
    weight_on_bit_kn: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    rotary_rpm: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    torque_kn_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    rate_of_penetration_m_hr: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    standpipe_pressure_kpa: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    flow_rate_lpm: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    mud_weight_kg_m3: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    mud_viscosity_cp: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)

    well: Mapped[Well] = relationship(back_populates="parameters")
    __table_args__ = (Index("ix_drilling_parameters_well_time", "well_id", "recorded_at"),)


class GeologicalInformation(Base, TimestampMixin):
    __tablename__ = "geological_information"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    depth_from_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    depth_to_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    lithology: Mapped[str | None] = mapped_column(String(255))
    porosity_pct: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    permeability_md: Mapped[Decimal | None] = mapped_column(Numeric(14, 5))
    pressure_kpa: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    temperature_c: Mapped[Decimal | None] = mapped_column(Numeric(8, 3))
    properties: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    well: Mapped[Well] = relationship(back_populates="geological_information")


class Formation(Base, TimestampMixin):
    __tablename__ = "formations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    formation_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    top_depth_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    base_depth_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    lithology: Mapped[str | None] = mapped_column(String(255))
    age: Mapped[str | None] = mapped_column(String(100))
    stratigraphic_group: Mapped[str | None] = mapped_column(String(255))
    properties: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    well: Mapped[Well] = relationship(back_populates="formations")
    __table_args__ = (Index("ix_formations_well_depth", "well_id", "top_depth_m", "base_depth_m"),)


class DrillingEvent(Base, TimestampMixin):
    __tablename__ = "drilling_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    depth_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), index=True)
    severity: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    duration_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    well: Mapped[Well] = relationship(back_populates="events")
    __table_args__ = (Index("ix_drilling_events_well_time", "well_id", "event_time"),)


class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    document_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    well_id: Mapped[str | None] = mapped_column(ForeignKey("wells.id", ondelete="SET NULL"), index=True)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(500))
    storage_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    page_count: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    well: Mapped[Well | None] = relationship(back_populates="documents")
    chunks: Mapped[list[DocumentChunk]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer)
    formation: Mapped[str | None] = mapped_column(String(255), index=True)
    depth_from_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    depth_to_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    event_type: Mapped[str | None] = mapped_column(String(100), index=True)
    qdrant_point_id: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    document: Mapped[Document] = relationship(back_populates="chunks")
    __table_args__ = (UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),)


class ModelVersion(Base, TimestampMixin):
    __tablename__ = "model_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(100), nullable=False)
    artifact_uri: Mapped[str | None] = mapped_column(String(1000))
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    feature_schema: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    predictions: Mapped[list[Prediction]] = relationship(back_populates="model_version")
    __table_args__ = (UniqueConstraint("model_name", "version", name="uq_model_version"),)


class Prediction(Base, TimestampMixin):
    __tablename__ = "predictions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    well_id: Mapped[str] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    model_version_id: Mapped[str | None] = mapped_column(ForeignKey("model_versions.id", ondelete="SET NULL"), index=True)
    prediction_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    predicted_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    risk_score: Mapped[Decimal | None] = mapped_column(Numeric(7, 6))
    severity: Mapped[str | None] = mapped_column(String(50))
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    explanation: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    input_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    well: Mapped[Well] = relationship(back_populates="predictions")
    model_version: Mapped[ModelVersion | None] = relationship(back_populates="predictions")


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    well_id: Mapped[str | None] = mapped_column(ForeignKey("wells.id", ondelete="SET NULL"), index=True)
    prediction_id: Mapped[str | None] = mapped_column(ForeignKey("predictions.id", ondelete="SET NULL"), index=True)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    well: Mapped[Well | None] = relationship(back_populates="alerts")


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    well_id: Mapped[str | None] = mapped_column(ForeignKey("wells.id", ondelete="SET NULL"), index=True)
    prediction_id: Mapped[str | None] = mapped_column(ForeignKey("predictions.id", ondelete="SET NULL"), index=True)
    recommendation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[str | None] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="NEW", nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    well: Mapped[Well | None] = relationship(back_populates="recommendations")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(100), default="ENGINEER", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
