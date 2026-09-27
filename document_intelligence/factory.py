"""Factory for constructing a configured document intelligence pipeline."""
from __future__ import annotations

from .config import DocumentIntelligenceConfig
from .pipeline import DocumentIntelligencePipeline


def create_pipeline(config: DocumentIntelligenceConfig | None = None) -> DocumentIntelligencePipeline:
    """Create the pipeline using environment configuration and an optional OCR adapter."""
    config = config or DocumentIntelligenceConfig.from_env()
    adapter = None
    if config.ocr_engine == "tesseract":
        from .ocr.tesseract_adapter import TesseractOCR
        adapter = TesseractOCR(lang=config.ocr_lang)
    elif config.ocr_engine == "paddleocr":
        from .ocr.paddle_adapter import PaddleOCREngine
        # PaddleOCR language codes differ from Tesseract codes. `en` is the
        # expected value for the default English configuration.
        adapter = PaddleOCREngine(lang="en" if config.ocr_lang == "eng" else config.ocr_lang)
    elif config.ocr_engine not in {"none", ""}:
        raise ValueError(f"Unsupported NWIS_DI_OCR_ENGINE: {config.ocr_engine}")
    return DocumentIntelligencePipeline(ocr_adapter=adapter, min_native_chars=config.min_native_chars, dpi=config.dpi, max_file_size_bytes=config.max_file_size_mb * 1024 * 1024)
