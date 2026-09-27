"""Deterministic page/section segmentation."""
from __future__ import annotations
import re

_HEADING = re.compile(r"^(?:\d+(?:\.\d+)*[.)]?\s+)?[A-Z][A-Z0-9 /&()_-]{2,80}$")


def clean_text(text: str) -> str:
    """Normalize extracted text while preserving line boundaries."""
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def segment_pages(pages: list[dict], document_id: str, file_name: str, source_type: str) -> list[dict]:
    """Segment page text using heading-like lines; no semantic model is used."""
    sections: list[dict] = []
    current: dict | None = None
    sequence = 0
    for page in pages:
        page_number = page["page_number"]
        lines = [line.strip() for line in page["text"].splitlines() if line.strip()]
        for line in lines:
            is_heading = bool(_HEADING.match(line)) and len(line.split()) <= 12
            if is_heading:
                if current:
                    current["text"] = clean_text(current["text"])
                    current["page_end"] = page_number
                    sections.append(current)
                sequence += 1
                current = {
                    "section_id": f"SEC-{sequence:04d}",
                    "title": line,
                    "text": "",
                    "page_start": page_number,
                    "page_end": page_number,
                    "provenance": {
                        "document_id": document_id,
                        "file_name": file_name,
                        "page_number": page_number,
                        "section": line,
                        "source_type": source_type,
                    },
                }
            elif current is not None:
                current["text"] += line + "\n"
        if current:
            current["page_end"] = page_number
    if current:
        current["text"] = clean_text(current["text"])
        sections.append(current)
    if not sections:
        for page in pages:
            if page["text"].strip():
                sequence += 1
                sections.append({
                    "section_id": f"SEC-{sequence:04d}",
                    "title": f"Page {page['page_number']}",
                    "text": page["text"],
                    "page_start": page["page_number"],
                    "page_end": page["page_number"],
                    "provenance": {
                        "document_id": document_id,
                        "file_name": file_name,
                        "page_number": page["page_number"],
                        "section": f"Page {page['page_number']}",
                        "source_type": source_type,
                    },
                })
    return sections
