"""Public NLP information-extraction pipeline."""
from __future__ import annotations

import logging
from typing import Optional

from .extractors import RuleBasedExtractor
from .models import DocumentInput, ExtractionResult

logger = logging.getLogger(__name__)


class DrillingNLPExtractor:
    """Convert document-processor output into structured drilling knowledge.

    Rule-based extraction is always available. spaCy and Transformer NER are
    optional enrichers and are intentionally isolated behind adapters.
    """

    def __init__(self, *, spacy_model: Optional[str] = None, transformer_model: Optional[str] = None) -> None:
        self.rules = RuleBasedExtractor()
        self.spacy = None
        self.transformer = None
        if spacy_model:
            from .extractors.spacy_ner import SpacyNERExtractor
            self.spacy = SpacyNERExtractor(spacy_model)
        if transformer_model:
            from .extractors.transformer_ner import TransformerNERExtractor
            self.transformer = TransformerNERExtractor(transformer_model)

    def extract(self, document: DocumentInput) -> ExtractionResult:
        """Extract all supported drilling facts while retaining page/source provenance."""
        result = ExtractionResult(document_id=document.document_id)
        for page in document.pages:
            try:
                result.entities.extend(self.rules.extract_entities(document.document_id, page))
                result.events.extend(self.rules.extract_events(document.document_id, page))
                result.formation_observations.extend(self.rules.extract_formations(document.document_id, page))
                result.mitigation_actions.extend(self.rules.extract_actions(document.document_id, page))
                result.lessons_learned.extend(self.rules.extract_lessons(document.document_id, page))
                if self.spacy:
                    result.entities.extend(self.spacy.extract(document.document_id, page))
                if self.transformer:
                    result.entities.extend(self.transformer.extract(document.document_id, page))
            except Exception:
                logger.exception("NLP extraction failed for document=%s page=%s", document.document_id, page.page_number)
                raise
        result.processing_metadata = {
            "extractor": "RuleBasedExtractor",
            "spacy_enabled": self.spacy is not None,
            "transformer_enabled": self.transformer is not None,
        }
        return result
