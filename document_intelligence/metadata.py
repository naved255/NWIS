"""Best-effort metadata extraction without semantic RAG."""
from __future__ import annotations
import re
from pathlib import Path

WELL_PATTERNS = [
    re.compile(r"\bwell\s*(?:id|no|number)\s*[:#-]?\s*([A-Z0-9][A-Z0-9._/-]{2,})", re.I),
    re.compile(r"\bwell\s*[:#-]\s*([A-Z0-9][A-Z0-9._/-]{2,})", re.I),
    re.compile(r"\b([A-Z]{1,5}[-_/][A-Z0-9]{2,})\b"),
]
DATE_PATTERN = re.compile(r"\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b|\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b")


def infer_document_type(path: str | Path, text: str = "") -> str:
    """Infer a document type from filename and common report labels."""
    value = Path(path).name.upper() + "\n" + text[:10000].upper()
    for key, label in (("DDR", "DDR"), ("DAILY DRILLING", "DDR"), ("WCR", "WCR"), ("WELL COMPLETION", "WCR"), ("COMPLETION REPORT", "WCR"), ("MUD LOG", "MUD_LOG"), ("OPERATION", "OPERATIONAL_REPORT")):
        if key in value:
            return label
    return "OTHER"


def infer_metadata(path: str | Path, text: str, document_type: str) -> dict:
    """Extract conservative metadata fields using deterministic patterns."""
    well_id = None
    for pattern in WELL_PATTERNS:
        match = pattern.search(text)
        if match:
            well_id = next((g for g in match.groups() if g), None)
            if well_id:
                break
    date_match = DATE_PATTERN.search(text)
    report_date = next((g for g in date_match.groups() if g), None) if date_match else None
    return {
        "title": Path(path).stem,
        "well_id": well_id,
        "document_type": document_type,
        "report_date": report_date,
        "operator": None,
        "source_type": document_type,
    }
