"""JSON data source."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .base import DataSource


class JSONDataSource(DataSource):
    """Read JSON records from an object or an array.

    If the root is an object, ``records_key`` may point to a list under that key.
    """

    def __init__(self, path: str | Path, *, source_name: str | None = None, records_key: str = "records"):
        self.path = Path(path)
        self.source_name = source_name or self.path.name
        self.records_key = records_key

    @property
    def metadata(self) -> dict[str, Any]:
        return {"source_type": "json", "source_name": self.source_name, "source_uri": self.path.resolve().as_uri()}

    def read(self):
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict) and isinstance(payload.get(self.records_key), list):
            records = payload[self.records_key]
        elif isinstance(payload, dict):
            records = [payload]
        else:
            raise ValueError("JSON root must be an object or array of objects")
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Every JSON record must be an object")
            yield record
