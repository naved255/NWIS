"""Pipeline result models."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from .entities import NWISEntity


class IngestionError(BaseModel):
    """Validation/processing error for one source record."""
    record_index: int
    error_type: str
    message: str
    raw_record: dict[str, Any] = Field(default_factory=dict)


class IngestionResult(BaseModel):
    """Summary returned by the ingestion engine."""
    entity_type: str
    accepted: list[NWISEntity] = Field(default_factory=list)
    duplicates: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[IngestionError] = Field(default_factory=list)
    total_records: int = 0

    @property
    def accepted_count(self) -> int:
        return len(self.accepted)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicates)

    @property
    def error_count(self) -> int:
        return len(self.errors)
