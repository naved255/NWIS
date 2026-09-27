from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import DrillingParameterUpdate


FIELD_ALIASES = {
    "depth_m": "depth",
    "measured_depth": "depth",
    "rop_m_per_hr": "rop",
    "rate_of_penetration": "rop",
    "weight_on_bit": "wob",
    "rotary_speed": "rpm",
    "pump_pressure": "pressure",
    "mud_flow_rate": "mud_flow",
    "mud_weight_ppg": "mud_weight",
}

REQUIRED_FIELDS = ("depth", "rop", "wob", "rpm", "torque", "pressure", "mud_flow", "mud_weight")


def normalize_update(payload: dict[str, Any], well_id: str | None = None) -> DrillingParameterUpdate:
    """Map provider-specific field names into the NWIS canonical schema."""
    data = dict(payload)
    for source, target in FIELD_ALIASES.items():
        if target not in data and source in data:
            data[target] = data[source]

    if well_id is not None:
        data["well_id"] = well_id
    if "timestamp" not in data:
        data["timestamp"] = datetime.now(timezone.utc)

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        raise ValueError(f"Missing required real-time fields: {', '.join(missing)}")

    return DrillingParameterUpdate.model_validate(data)
