"""Field-name normalization and source aliases."""
from __future__ import annotations
import re
from typing import Any

ALIASES = {
    "wellid": "well_id", "well_id": "well_id", "wellno": "well_id", "well_number": "well_id",
    "wellname": "well_name", "well_name": "well_name",
    "field": "field_name", "fieldname": "field_name", "field_name": "field_name",
    "lat": "latitude", "latitude": "latitude", "lon": "longitude", "long": "longitude", "longitude": "longitude",
    "md": "measured_depth", "measureddepth": "measured_depth", "measured_depth": "measured_depth",
    "tvd": "true_vertical_depth", "trueverticaldepth": "true_vertical_depth", "true_vertical_depth": "true_vertical_depth",
    "inc": "inclination", "inclination": "inclination", "azi": "azimuth", "azimuth": "azimuth",
    "date": "observed_at", "datetime": "observed_at", "timestamp": "observed_at", "time": "observed_at",
    "rop_mph": "rop", "rop": "rop", "wob_klbf": "wob", "wob": "wob", "rpm": "rpm",
    "mudweight": "mud_weight", "mud_weight": "mud_weight", "mw": "mud_weight",
    "flow_rate": "mud_flow_rate", "mudflowrate": "mud_flow_rate", "pump_rate": "mud_flow_rate",
    "spp": "standpipe_pressure", "standpipepressure": "standpipe_pressure",
    "event": "event_type", "event_type": "event_type", "eventid": "event_id", "event_id": "event_id",
    "description": "description", "depth": "depth", "totaldepth": "total_depth", "total_depth": "total_depth",
    "documentid": "document_id", "document_id": "document_id", "filename": "file_name", "file_name": "file_name",
}

MISSING = {"", "na", "n/a", "none", "null", "nan", "-", "--"}


def normalize_field_name(name: str) -> str:
    """Convert a source field name to canonical snake_case, applying aliases."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", str(name).strip()).strip("_").lower()
    compact = cleaned.replace("_", "")
    return ALIASES.get(cleaned, ALIASES.get(compact, cleaned))


def normalize_value(value: Any) -> Any:
    """Convert common missing-value markers to ``None`` while preserving data types."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in MISSING:
        return None
    return value


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize keys and common missing values in one raw record."""
    result: dict[str, Any] = {}
    for key, value in record.items():
        canonical = normalize_field_name(key)
        value = normalize_value(value)
        if canonical not in result or result[canonical] is None:
            result[canonical] = value
    return result
