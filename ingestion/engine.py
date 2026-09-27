"""Independent NWIS ingestion pipeline."""
from __future__ import annotations
import hashlib
import json
import logging
from typing import Any
from .normalizers import normalize_record
from .models import IngestionError, IngestionResult, SourceMetadata
from .readers import DataSource
from .validators import EntityValidator

logger = logging.getLogger(__name__)


class IngestionEngine:
    """Normalize, enrich, validate, and de-duplicate records from any DataSource."""

    def __init__(self, validator: EntityValidator | None = None):
        self.validator = validator or EntityValidator()

    @staticmethod
    def _fingerprint(entity: Any) -> str:
        """Create a deterministic content fingerprint excluding source metadata."""
        payload = entity.model_dump(mode="json", exclude={"source_metadata"})
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _source_metadata(source: DataSource, raw: dict[str, Any]) -> SourceMetadata:
        metadata = dict(source.metadata)
        record_id = raw.get("source_record_id") or raw.get("record_id") or raw.get("id")
        return SourceMetadata(**metadata, source_record_id=str(record_id) if record_id is not None else None)

    def ingest(self, source: DataSource, entity_type: str) -> IngestionResult:
        """Ingest all records from ``source`` as the requested canonical entity type."""
        result = IngestionResult(entity_type=entity_type)
        seen: set[str] = set()
        try:
            iterator = source.read()
            for index, raw in enumerate(iterator):
                result.total_records += 1
                try:
                    if not isinstance(raw, dict):
                        raise TypeError("source record must be a dictionary")
                    normalized = normalize_record(raw)
                    normalized["source_metadata"] = self._source_metadata(source, raw)
                    entity = self.validator.validate(entity_type, normalized)
                    fingerprint = self._fingerprint(entity)
                    if fingerprint in seen:
                        result.duplicates.append({"record_index": index, "fingerprint": fingerprint})
                        continue
                    seen.add(fingerprint)
                    result.accepted.append(entity)
                except Exception as exc:  # validation errors are isolated per record
                    logger.warning("Rejected %s record %d: %s", entity_type, index, exc)
                    result.errors.append(IngestionError(
                        record_index=index,
                        error_type=type(exc).__name__,
                        message=str(exc),
                        raw_record=raw if isinstance(raw, dict) else {},
                    ))
        except Exception as exc:
            logger.exception("Source read failed for %s", entity_type)
            result.errors.append(IngestionError(record_index=-1, error_type=type(exc).__name__, message=str(exc)))
        return result
