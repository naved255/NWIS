"""Database ingestion adapter with a deliberately small interface."""
from __future__ import annotations
from collections.abc import Callable, Iterator
from typing import Any
from ..readers.base import DataSource


class DatabaseDataSource(DataSource):
    """Read mappings from a database through an injected query function.

    The injected callable keeps ingestion independent from a specific database
    driver/ORM. For SQLAlchemy, pass ``connection.execute(...).mappings()``
    through a small wrapper in the application layer.
    """

    def __init__(self, query_executor: Callable[[], Iterator[dict[str, Any]]], *, source_name: str = "database", source_uri: str | None = None):
        self.query_executor = query_executor
        self.source_name = source_name
        self.source_uri = source_uri

    @property
    def metadata(self) -> dict[str, Any]:
        return {"source_type": "database", "source_name": self.source_name, "source_uri": self.source_uri}

    def read(self):
        for row in self.query_executor():
            yield dict(row)
