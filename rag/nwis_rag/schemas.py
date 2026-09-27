"""Pydantic contracts for the NWIS historical knowledge RAG module."""

from __future__ import annotations

from datetime import date as Date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RetrievalFilters(BaseModel):
    """Optional Qdrant metadata filters."""

    model_config = ConfigDict(extra="forbid")

    well_id: str | None = None
    formation: str | None = None
    depth_min: float | None = Field(default=None, ge=0)
    depth_max: float | None = Field(default=None, ge=0)
    event_type: str | None = None
    document_type: str | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    location: str | None = None

    @field_validator("depth_max")
    @classmethod
    def depth_range_is_valid(cls, value: float | None, info: Any) -> float | None:
        minimum = info.data.get("depth_min")
        if value is not None and minimum is not None and value < minimum:
            raise ValueError("depth_max must be greater than or equal to depth_min")
        return value


class RetrievalQuery(BaseModel):
    """Input to a retrieval operation."""

    query: str = Field(min_length=1)
    filters: RetrievalFilters = Field(default_factory=RetrievalFilters)
    top_k: int = Field(default=8, ge=1, le=100)
    score_threshold: float | None = Field(default=None, ge=0, le=1)
    target_well_id: str | None = None


class ChunkRecord(BaseModel):
    """A document chunk ready for embedding and indexing."""

    chunk_id: str
    text: str = Field(min_length=1)
    source_uri: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    well_id: str | None = None
    formation: str | None = None
    depth: float | None = None
    depth_top: float | None = None
    depth_bottom: float | None = None
    event_type: str | None = None
    document_type: str | None = None
    date: Date | None = None
    location: str | None = None
    page: int | None = None
    extra_metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceItem(BaseModel):
    """A retrieved factual evidence item with a traceable source."""

    evidence_id: str
    text: str
    score: float
    source_uri: str
    source_name: str
    page: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def source_reference(self) -> str:
        """Return a human-readable source reference."""
        if self.page is not None:
            return f"{self.source_name}, page {self.page} ({self.source_uri})"
        return f"{self.source_name} ({self.source_uri})"


class RetrievalResponse(BaseModel):
    """Retrieval output returned to another NWIS module."""

    query: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    sufficient_evidence: bool
    message: str | None = None


class AnswerResponse(BaseModel):
    """Evidence-grounded answer with explicit fact/source/inference separation."""

    question: str
    fact: list[str] = Field(default_factory=list)
    source: list[str] = Field(default_factory=list)
    inference: list[str] = Field(default_factory=list)
    sufficient_evidence: bool
    message: str | None = None


class SearchMode(str):
    """Supported retrieval modes."""

    DOCUMENTS = "documents"
    EVENTS = "events"
    OFFSET_WELLS = "offset_wells"
