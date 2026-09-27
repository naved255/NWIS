"""HTTP API ingestion adapter."""
from __future__ import annotations
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from typing import Any
from ..readers.base import DataSource


class APIDataSource(DataSource):
    """Fetch JSON records from an HTTP API.

    Authentication headers/tokens are supplied by the caller and should come from
    environment variables or a secret manager, not source code.
    """

    def __init__(self, url: str, *, source_name: str = "api", headers: dict[str, str] | None = None,
                 params: dict[str, str] | None = None, timeout: float = 30.0, records_key: str = "records"):
        self.url, self.source_name, self.headers = url, source_name, headers or {}
        self.params, self.timeout, self.records_key = params or {}, timeout, records_key

    @property
    def metadata(self) -> dict[str, Any]:
        return {"source_type": "api", "source_name": self.source_name, "source_uri": self.url}

    def read(self):
        target = self.url
        if self.params:
            target += ("&" if "?" in target else "?") + urlencode(self.params)
        request = Request(target, headers={"Accept": "application/json", **self.headers}, method="GET")
        with urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - URL is configured by caller
            payload = json.loads(response.read().decode("utf-8"))
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict) and isinstance(payload.get(self.records_key), list):
            records = payload[self.records_key]
        elif isinstance(payload, dict):
            records = [payload]
        else:
            raise ValueError("API response must be a JSON object or array")
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("API records must be JSON objects")
            yield record
