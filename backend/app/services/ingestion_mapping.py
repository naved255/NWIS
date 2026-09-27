"""Explicit mapping between canonical ingestion entities and NWIS DB column names."""
from __future__ import annotations

from typing import Any


def well_to_db_values(entity: Any) -> dict[str, Any]:
    return {
        "well_id": entity.well_id,
        "well_name": entity.well_name,
        "field_name": entity.field_name,
        "block_name": entity.block,
        "operator": entity.operator,
        "latitude": entity.latitude,
        "longitude": entity.longitude,
        "spud_date": entity.spud_date,
        "completion_date": entity.completion_date,
        "status": entity.status,
        "total_depth_m": entity.total_depth,
        "metadata_json": {"basin": entity.basin, "source_metadata": entity.source_metadata.model_dump(mode="json")},
    }


def drilling_parameter_to_db_values(entity: Any) -> dict[str, Any]:
    return {
        "recorded_at": entity.observed_at,
        "measured_depth_m": entity.depth,
        "rate_of_penetration_m_hr": entity.rop,
        "weight_on_bit_kn": entity.wob,
        "rotary_rpm": entity.rpm,
        "torque_kn_m": entity.torque,
        "flow_rate_lpm": entity.mud_flow_rate,
        "standpipe_pressure_kpa": entity.standpipe_pressure,
        "mud_weight_kg_m3": entity.mud_weight,
        "metadata_json": {"hookload": entity.hookload, "pump_pressure": entity.pump_pressure, "temperature": entity.temperature, "bit_size": entity.bit_size, "bit_type": entity.bit_type},
    }


def drilling_event_to_db_values(entity: Any) -> dict[str, Any]:
    return {
        "id": entity.event_id,
        "event_type": entity.event_type,
        "event_time": entity.occurred_at,
        "depth_m": entity.depth,
        "severity": entity.severity,
        "description": entity.description,
        "duration_min": entity.duration_minutes,
        "metadata_json": {**entity.attributes, "source_metadata": entity.source_metadata.model_dump(mode="json")},
    }
