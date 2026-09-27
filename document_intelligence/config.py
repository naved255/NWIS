"""Environment-based configuration for document intelligence."""
from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentIntelligenceConfig:
    """Runtime configuration loaded from environment variables."""
    ocr_engine: str = "none"
    ocr_lang: str = "eng"
    min_native_chars: int = 20
    dpi: int = 200
    max_file_size_mb: int = 100

    @classmethod
    def from_env(cls) -> "DocumentIntelligenceConfig":
        """Build configuration from `NWIS_DI_*` environment variables."""
        return cls(
            ocr_engine=os.getenv("NWIS_DI_OCR_ENGINE", "none").lower(),
            ocr_lang=os.getenv("NWIS_DI_OCR_LANG", "eng"),
            min_native_chars=int(os.getenv("NWIS_DI_MIN_NATIVE_CHARS", "20")),
            dpi=int(os.getenv("NWIS_DI_DPI", "200")),
            max_file_size_mb=int(os.getenv("NWIS_DI_MAX_FILE_SIZE_MB", "100")),
        )
