"""CSV data source."""
from __future__ import annotations
import csv
from pathlib import Path
from typing import Any
from .base import DataSource


class CSVDataSource(DataSource):
    """Read CSV rows lazily as dictionaries."""

    def __init__(self, path: str | Path, *, source_name: str | None = None, encoding: str = "utf-8-sig"):
        self.path = Path(path)
        self.source_name = source_name or self.path.name
        self.encoding = encoding

    @property
    def metadata(self) -> dict[str, Any]:
        return {"source_type": "csv", "source_name": self.source_name, "source_uri": self.path.resolve().as_uri()}

    def read(self):
        with self.path.open("r", encoding=self.encoding, newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError(f"CSV file has no header: {self.path}")
            yield from reader
