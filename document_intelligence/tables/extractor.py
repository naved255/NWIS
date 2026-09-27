"""Table extraction adapters."""
from __future__ import annotations
from typing import Any


def extract_tables_from_page(page: Any) -> list[dict]:
    """Extract tables from a PyMuPDF page when supported, with pdfplumber fallback."""
    tables: list[dict] = []
    finder = getattr(page, "find_tables", None)
    if callable(finder):
        try:
            found = finder()
            for index, table in enumerate(getattr(found, "tables", []), start=1):
                data = table.extract()
                tables.append({"index": index, "data": data or [], "method": "pymupdf"})
            if tables:
                return tables
        except Exception:
            pass

    # pdfplumber fallback requires a file-backed page object and is handled by
    # the pipeline's fallback path. This function intentionally has no global file state.
    return tables


def normalize_table(data: list[list[Any]]) -> tuple[list[str], list[list[str]], list[dict]]:
    """Normalize raw table cells to strings and separate a header row."""
    cleaned = [["" if cell is None else str(cell).strip() for cell in row] for row in data if row]
    if not cleaned:
        return [], [], []
    width = max(len(row) for row in cleaned)
    cleaned = [row + [""] * (width - len(row)) for row in cleaned]
    headers = cleaned[0]
    rows = cleaned[1:]
    cells = [
        {"row": r, "column": c, "value": value}
        for r, row in enumerate(cleaned)
        for c, value in enumerate(row)
    ]
    return headers, rows, cells


def extract_tables_with_pdfplumber(pdf_path: str, page_number: int) -> list[dict]:
    """Extract tables from one PDF page using optional pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        return []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_number - 1]
            tables = []
            for index, data in enumerate(page.extract_tables() or [], start=1):
                tables.append({"index": index, "data": data or [], "method": "pdfplumber"})
            return tables
    except Exception:
        return []
