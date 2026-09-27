"""Reader interfaces for tabular/structured sources."""
from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any


class DataSource(ABC):
    """Common interface implemented by every ingestion source."""

    @property
    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        """Return source metadata attached to each record."""

    @abstractmethod
    def read(self) -> Iterator[dict[str, Any]]:
        """Yield raw records as dictionaries."""
