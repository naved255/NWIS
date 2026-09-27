from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RealtimeSettings(BaseSettings):
    """Environment-driven configuration for the real-time module."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    adapter: str = Field(default="mock", alias="NWIS_ERTMAC_ADAPTER")
    mock_interval_seconds: float = Field(default=1.0, alias="NWIS_REALTIME_INTERVAL_SECONDS", gt=0)
    mock_seed: int = Field(default=42, alias="NWIS_REALTIME_MOCK_SEED")
    abnormal_detection_enabled: bool = Field(default=True, alias="NWIS_REALTIME_ABNORMAL_DETECTION")


@lru_cache(maxsize=1)
def get_settings() -> RealtimeSettings:
    return RealtimeSettings()
