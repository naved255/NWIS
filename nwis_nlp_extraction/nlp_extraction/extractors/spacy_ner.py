"""Optional spaCy NER adapter. The core pipeline remains dependency-light."""
from __future__ import annotations

from typing import List, Optional

from ..models import DocumentPage, ExtractedEntity, Provenance


class SpacyNERExtractor:
    """Extract model-recognized entities when a spaCy model is available."""

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        try:
            import spacy
        except ImportError as exc:
            raise RuntimeError("spaCy is not installed. Install the optional nlp extra.") from exc
        try:
            self.nlp = spacy.load(model_name)
        except OSError as exc:
            raise RuntimeError(f"spaCy model '{model_name}' is not installed.") from exc

    def extract(self, document_id: str, page: DocumentPage) -> List[ExtractedEntity]:
        doc = self.nlp(page.text)
        out: List[ExtractedEntity] = []
        for ent in doc.ents:
            # Keep generic model output separate from drilling-specific rules.
            out.append(ExtractedEntity(
                entity_type=f"SPACY_{ent.label_}", value=ent.text,
                normalized_value=ent.text.strip(), confidence=0.65,
                provenance=Provenance(document_id=document_id, page_number=page.page_number,
                    text_span=[ent.start_char, ent.end_char], source_text=ent.text),
            ))
        return out
