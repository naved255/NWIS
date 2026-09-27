from __future__ import annotations

from .adapters import ERTMACAdapter, MockERTMACAdapter
from .config import RealtimeSettings


def create_ertmac_adapter(settings: RealtimeSettings | None = None) -> ERTMACAdapter:
    """Create the configured eRTMAC provider adapter."""
    settings = settings or RealtimeSettings()
    if settings.adapter.lower() == "mock":
        return MockERTMACAdapter(interval_seconds=settings.mock_interval_seconds, seed=settings.mock_seed)
    raise ValueError(
        f"Unsupported NWIS_ERTMAC_ADAPTER={settings.adapter!r}. "
        "Register a production adapter in the factory without changing the downstream pipeline."
    )
