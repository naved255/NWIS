"""PDF adapter interface; OCR/NLP extraction is intentionally delegated elsewhere."""
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from ..readers.base import DataSource


class PDFDataSource(DataSource, ABC):
    """Contract for PDF metadata/content adapters.

    Implementations may use PyMuPDF, OCR, or a document-extraction service in a
    separate module. This package only defines the boundary and metadata flow.
    """

    def __init__(self, path: str | Path, *, source_name: str | None = None):
        self.path = Path(path)
        self.source_name = source_name or self.path.name

    @property
    def metadata(self) -> dict[str, Any]:
        return {"source_type": "pdf", "source_name": self.source_name, "source_uri": self.path.resolve().as_uri()}

    @abstractmethod
    def read(self):
        """Yield document metadata or extracted records supplied by an external adapter."""


class PDFMetadataAdapter(PDFDataSource):
    """Minimal PDF adapter that emits metadata without OCR/NLP."""

    def read(self):
        stat = self.path.stat()
        yield {
            "document_id": self.path.stem,
            "document_type": "unknown",
            "file_name": self.path.name,
            "mime_type": "application/pdf",
            "file_size_bytes": stat.st_size,
            "extraction_status": "not_extracted",
        }
