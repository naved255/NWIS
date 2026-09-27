"""Pydantic schemas for structured drilling knowledge and provenance."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    MUD_LOSS = "MUD_LOSS"
    KICK = "KICK"
    STUCK_PIPE = "STUCK_PIPE"
    FISHING = "FISHING"
    NPT = "NPT"
    CEMENTING_PROBLEM = "CEMENTING_PROBLEM"
    PRESSURE_OBSERVATION = "PRESSURE_OBSERVATION"
    CASING_EVENT = "CASING_EVENT"
    OTHER = "OTHER"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class Provenance(BaseModel):
    """Source location for an extracted fact."""

    model_config = ConfigDict(extra="forbid")
    document_id: str
    page_number: Optional[int] = None
    text_span: Optional[List[int]] = Field(default=None, description="Character offsets [start, end] in source_text.")
    source_text: str


class ExtractedEntity(BaseModel):
    """Generic named/value entity extracted from a document."""

    model_config = ConfigDict(extra="forbid")
    entity_type: str
    value: str
    normalized_value: Optional[str] = None
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    provenance: Provenance
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DrillingEvent(BaseModel):
    """Contextually validated drilling event."""

    model_config = ConfigDict(extra="forbid")
    event_type: EventType
    depth_m: Optional[float] = None
    severity: Severity = Severity.UNKNOWN
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    description: str
    date: Optional[str] = None
    mitigation_action_ids: List[str] = Field(default_factory=list)
    provenance: Provenance
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FormationObservation(BaseModel):
    """Observation linking a geological formation to drilling context."""

    model_config = ConfigDict(extra="forbid")
    formation_name: str
    depth_m: Optional[float] = None
    observation: Optional[str] = None
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    provenance: Provenance


class MitigationAction(BaseModel):
    """Action taken or recommended to mitigate a drilling issue."""

    model_config = ConfigDict(extra="forbid")
    action: str
    action_type: str = "MITIGATION"
    related_event_type: Optional[EventType] = None
    is_recommendation: bool = False
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    provenance: Provenance


class LessonLearned(BaseModel):
    """Lesson learned or operational takeaway."""

    model_config = ConfigDict(extra="forbid")
    lesson: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    provenance: Provenance


class DocumentInput(BaseModel):
    """Normalized input from the document-processing module."""

    model_config = ConfigDict(extra="forbid")
    document_id: str
    pages: List["DocumentPage"]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentPage(BaseModel):
    page_number: int
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    """Complete NLP extraction output."""

    model_config = ConfigDict(extra="forbid")
    document_id: str
    entities: List[ExtractedEntity] = Field(default_factory=list)
    events: List[DrillingEvent] = Field(default_factory=list)
    formation_observations: List[FormationObservation] = Field(default_factory=list)
    mitigation_actions: List[MitigationAction] = Field(default_factory=list)
    lessons_learned: List[LessonLearned] = Field(default_factory=list)
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
