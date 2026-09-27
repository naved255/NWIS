"""Optional Hugging Face token-classification adapter."""
from __future__ import annotations

from typing import List

from ..models import DocumentPage, ExtractedEntity, Provenance


class TransformerNERExtractor:
    """Run a Hugging Face token-classification model if configured."""

    def __init__(self, model_name: str) -> None:
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError("Transformers is not installed. Install the optional nlp extra.") from exc
        self.pipeline = pipeline("token-classification", model=model_name, aggregation_strategy="simple")

    def extract(self, document_id: str, page: DocumentPage) -> List[ExtractedEntity]:
        results = self.pipeline(page.text)
        out: List[ExtractedEntity] = []
        for item in results:
            start, end = int(item.get("start", 0)), int(item.get("end", 0))
            source = page.text[start:end]
            out.append(ExtractedEntity(
                entity_type=f"TRANSFORMER_{item.get('entity_group', item.get('entity', 'ENTITY'))}",
                value=source, normalized_value=source.strip(),
                confidence=float(item.get("score", 0.0)),
                provenance=Provenance(document_id=document_id, page_number=page.page_number,
                    text_span=[start, end], source_text=source),
            ))
        return out
