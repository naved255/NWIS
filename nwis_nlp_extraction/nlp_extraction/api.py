"""Optional FastAPI interface for the NLP extraction module."""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException

from .models import DocumentInput, ExtractionResult
from .pipeline import DrillingNLPExtractor

logger = logging.getLogger(__name__)
app = FastAPI(title="NWIS NLP Information Extraction", version="1.0.0")

_spacy_model = os.getenv("NWIS_SPACY_MODEL") or None
_transformer_model = os.getenv("NWIS_TRANSFORMER_NER_MODEL") or None
_extractor = DrillingNLPExtractor(spacy_model=_spacy_model, transformer_model=_transformer_model)


@app.get("/health")
def health() -> dict:
    """Return service health and optional NLP adapter status."""
    return {"status": "ok", "spacy_enabled": _extractor.spacy is not None,
            "transformer_enabled": _extractor.transformer is not None}


@app.post("/v1/nlp/extract", response_model=ExtractionResult)
def extract(document: DocumentInput) -> ExtractionResult:
    """Extract structured drilling knowledge from processed document pages."""
    try:
        return _extractor.extract(document)
    except Exception as exc:
        logger.exception("Extraction request failed for document=%s", document.document_id)
        raise HTTPException(status_code=500, detail="NLP extraction failed") from exc
