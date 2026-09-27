"""Pydantic models for the NWIS document intelligence output contract."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class Provenance(BaseModel):
    """Location of an extracted item in its source document."""
    document_id: str
    file_name: str
    page_number: int = Field(ge=1)
    section: str | None = None
    source_type: str


class Page(BaseModel):
    """Processed page containing text and extraction metadata."""
    page_number: int = Field(ge=1)
    text: str = ""
    text_extraction_method: Literal["native", "ocr", "none"]
    has_selectable_text: bool
    provenance: Provenance


class Section(BaseModel):
    """Heuristically segmented document section."""
    section_id: str
    title: str
    text: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    provenance: Provenance


class TableCell(BaseModel):
    """One normalized table cell."""
    row: int = Field(ge=0)
    column: int = Field(ge=0)
    value: str = ""


class ExtractedTable(BaseModel):
    """Normalized table with provenance."""
    table_id: str
    page_number: int = Field(ge=1)
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    cells: list[TableCell] = Field(default_factory=list)
    extraction_method: str
    provenance: Provenance


class DocumentMetadata(BaseModel):
    """Best-effort metadata inferred from filename/content."""
    model_config = ConfigDict(extra="allow")

    title: str | None = None
    well_id: str | None = None
    document_type: str | None = None
    report_date: str | None = None
    operator: str | None = None
    source_type: str | None = None


class StructuredDocument(BaseModel):
    """Standardized document object consumed by NLP/RAG modules."""
    document_id: str
    file_name: str
    well_id: str | None = None
    document_type: str
    pages: list[Page] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)
    tables: list[ExtractedTable] = Field(default_factory=list)
    metadata: DocumentMetadata
