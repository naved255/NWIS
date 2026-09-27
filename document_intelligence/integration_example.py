"""Minimal example showing how downstream NLP/RAG code can consume this module."""
from .pipeline import DocumentIntelligencePipeline
from .ocr.tesseract_adapter import TesseractOCR


def process_for_downstream(path: str) -> dict:
    """Return a JSON-compatible standardized document for downstream modules."""
    pipeline = DocumentIntelligencePipeline(ocr_adapter=TesseractOCR())
    document = pipeline.process(path)
    return document.model_dump(mode="json")
