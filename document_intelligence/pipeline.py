"""Historical drilling document processing pipeline."""
from __future__ import annotations
import hashlib
import logging
from pathlib import Path
from typing import Optional

import fitz
from PIL import Image

from .metadata import infer_document_type, infer_metadata
from .models import DocumentMetadata, ExtractedTable, Page, Provenance, Section, StructuredDocument
from .segmentation import clean_text, segment_pages
from .tables.extractor import extract_tables_from_page, extract_tables_with_pdfplumber, normalize_table
from .validators import validate_file
from .ocr.base import OCRAdapter

logger = logging.getLogger(__name__)


class DocumentIntelligencePipeline:
    """Convert historical drilling documents into a standardized representation.

    Native PDF text is preferred. Pages with insufficient/no selectable text are
    rendered to images and passed to the configured OCR adapter.
    """

    def __init__(self, ocr_adapter: Optional[OCRAdapter] = None, min_native_chars: int = 20, dpi: int = 200, max_file_size_bytes: int = 100 * 1024 * 1024) -> None:
        self.ocr_adapter = ocr_adapter
        self.min_native_chars = min_native_chars
        self.dpi = dpi
        self.max_file_size_bytes = max_file_size_bytes

    def process(self, path: str | Path, document_id: str | None = None, document_type: str | None = None) -> StructuredDocument:
        """Process a PDF or image and return the standardized NWIS document object."""
        file_path = validate_file(path, max_size_bytes=self.max_file_size_bytes)
        doc_id = document_id or self._document_id(file_path)
        source_type = document_type or infer_document_type(file_path)
        if file_path.suffix.lower() == ".pdf":
            pages, raw_tables = self._process_pdf(file_path, doc_id, source_type)
        else:
            pages, raw_tables = self._process_image(file_path, doc_id, source_type)

        combined_text = "\n".join(page.text for page in pages)
        final_type = document_type or infer_document_type(file_path, combined_text)
        metadata = infer_metadata(file_path, combined_text, final_type)
        sections = segment_pages([p.model_dump() for p in pages], doc_id, file_path.name, final_type)
        section_models = [Section(**item) for item in sections]
        table_models = self._build_tables(raw_tables, doc_id, file_path.name, final_type)
        return StructuredDocument(
            document_id=doc_id,
            file_name=file_path.name,
            well_id=metadata.get("well_id"),
            document_type=final_type,
            pages=pages,
            sections=section_models,
            tables=table_models,
            metadata=DocumentMetadata(**metadata),
        )

    def _process_pdf(self, path: Path, document_id: str, source_type: str) -> tuple[list[Page], list[dict]]:
        pages: list[Page] = []
        raw_tables: list[dict] = []
        with fitz.open(path) as pdf:
            for index, pdf_page in enumerate(pdf, start=1):
                native_text = clean_text(pdf_page.get_text("text"))
                has_selectable = len(native_text.strip()) >= self.min_native_chars
                method = "native"
                text = native_text
                if not has_selectable:
                    if self.ocr_adapter is None:
                        method = "none"
                        text = native_text
                        logger.warning("No selectable text and no OCR adapter configured: %s page %d", path.name, index)
                    else:
                        method = "ocr"
                        image = self._render_page(pdf_page)
                        try:
                            text = clean_text(self.ocr_adapter.extract_text(image))
                        except Exception:
                            logger.exception("OCR failed for %s page %d", path.name, index)
                            text = ""
                provenance = Provenance(document_id=document_id, file_name=path.name, page_number=index, section=None, source_type=source_type)
                pages.append(Page(page_number=index, text=text, text_extraction_method=method, has_selectable_text=has_selectable, provenance=provenance))
                page_tables = extract_tables_from_page(pdf_page)
                if not page_tables:
                    page_tables = extract_tables_with_pdfplumber(str(path), index)
                for table in page_tables:
                    table["page_number"] = index
                    raw_tables.append(table)
        return pages, raw_tables

    def _process_image(self, path: Path, document_id: str, source_type: str) -> tuple[list[Page], list[dict]]:
        if self.ocr_adapter is None:
            raise ValueError("An OCR adapter is required to process image documents")
        with Image.open(path) as image:
            text = clean_text(self.ocr_adapter.extract_text(image.convert("RGB")))
        provenance = Provenance(document_id=document_id, file_name=path.name, page_number=1, section=None, source_type=source_type)
        return [Page(page_number=1, text=text, text_extraction_method="ocr", has_selectable_text=False, provenance=provenance)], []

    def _render_page(self, page: fitz.Page) -> Image.Image:
        matrix = fitz.Matrix(self.dpi / 72, self.dpi / 72)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    @staticmethod
    def _document_id(path: Path) -> str:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        return f"DOC-{digest}"

    @staticmethod
    def _build_tables(raw_tables: list[dict], document_id: str, file_name: str, source_type: str) -> list[ExtractedTable]:
        result: list[ExtractedTable] = []
        for ordinal, raw in enumerate(raw_tables, start=1):
            headers, rows, cells = normalize_table(raw.get("data", []))
            page_number = int(raw["page_number"])
            result.append(ExtractedTable(
                table_id=f"TBL-{ordinal:04d}",
                page_number=page_number,
                headers=headers,
                rows=rows,
                cells=cells,
                extraction_method=raw.get("method", "unknown"),
                provenance=Provenance(document_id=document_id, file_name=file_name, page_number=page_number, section=None, source_type=source_type),
            ))
        return result
