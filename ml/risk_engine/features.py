from __future__ import annotations

from typing import Iterable, List, Optional
import numpy as np
import pandas as pd

DEFAULT_NUMERIC = [
    "depth", "rop", "wob", "rpm", "torque", "pressure", "mud_flow", "mud_weight",
    "inclination", "azimuth", "dogleg_severity", "nearby_well_count",
    "nearby_event_rate", "historical_risk_rate",
]
DEFAULT_CATEGORICAL = ["formation"]


def engineer_features(df: pd.DataFrame, numeric: Optional[Iterable[str]] = None,
                       categorical: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """Create leakage-safe point-in-time features from raw drilling observations.

    Features are computed row-wise only; no target-derived rolling statistics are created.
    Caller-supplied historical aggregates must already be calculated using past data only.
    """
    out = df.copy()
    numeric_cols = [c for c in (numeric or DEFAULT_NUMERIC) if c in out.columns]
    for c in numeric_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    if "depth" in out:
        out["depth_change_from_reference"] = out["depth"] - out.groupby("well_id")["depth"].transform("min") if "well_id" in out else out["depth"]
    if "pressure" in out and "depth" in out:
        out["pressure_per_depth"] = out["pressure"] / out["depth"].replace(0, np.nan)
    if "torque" in out and "wob" in out:
        out["torque_per_wob"] = out["torque"] / out["wob"].replace(0, np.nan)
    if "rop" in out and "rpm" in out:
        out["rop_per_rpm"] = out["rop"] / out["rpm"].replace(0, np.nan)
    if "mud_weight" in out and "pressure" in out:
        out["pressure_mud_weight_ratio"] = out["pressure"] / out["mud_weight"].replace(0, np.nan)
    return out.replace([np.inf, -np.inf], np.nan)


def infer_feature_columns(df: pd.DataFrame, target_column: str,
                          time_column: Optional[str], group_column: Optional[str]) -> List[str]:
    """Select numeric/categorical model features while excluding identifiers and targets."""
    excluded = {target_column}
    if time_column:
        excluded.add(time_column)
    if group_column:
        excluded.add(group_column)
    excluded.update({"event_id", "document_id", "well_name"})
    return [c for c in df.columns if c not in excluded]
