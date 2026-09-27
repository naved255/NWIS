"""Nearby/offset well intelligence service."""
from __future__ import annotations

import math
from collections import Counter
from statistics import mean
from typing import Any

from .geojson import wells_to_feature_collection, trajectories_to_feature_collection
from ..models.schemas import (
    NearbyWell,
    NearbyWellsResponse,
    SimilarOffsetWell,
    SimilarOffsetWellsResponse,
    SimilarityFactors,
    TrajectoryComparison,
    TrajectoryResponse,
    TrajectoryPoint,
    DepthRange,
)
from ..repositories.postgis import PostGISWellRepository


def _reservoirs(well: Any, formations: list[Any]) -> set[str]:
    values: set[str] = set()
    metadata = getattr(well, "metadata_json", None) or {}
    if isinstance(metadata, dict) and metadata.get("reservoir"):
        values.add(str(metadata["reservoir"]).strip())
    for formation in formations:
        props = getattr(formation, "properties", None) or {}
        if isinstance(props, dict) and props.get("reservoir"):
            values.add(str(props["reservoir"]).strip())
    return {v for v in values if v}


def _formations(formations: list[Any]) -> set[str]:
    return {str(f.formation_name).strip() for f in formations if f.formation_name}


def _depth_overlap(
    first_depth: float | None,
    second_depth: float | None,
    requested: tuple[float, float] | None = None,
) -> float:
    if first_depth is None or second_depth is None:
        return 0.0
    a0, a1 = (0.0, first_depth)
    b0, b1 = (0.0, second_depth)
    if requested:
        r0, r1 = sorted(requested)
        b0, b1 = max(b0, r0), min(b1, r1)
    return max(0.0, min(a1, b1) - max(a0, b0))


def _interval_overlap_score(
    active_depth: float | None,
    candidate_depth: float | None,
    requested: tuple[float, float] | None,
) -> float:
    if active_depth is None or candidate_depth is None:
        return 0.0
    overlap = _depth_overlap(active_depth, candidate_depth, requested)
    if requested:
        target_span = max(1.0, requested[1] - requested[0])
        return min(1.0, overlap / target_span)
    common = min(active_depth, candidate_depth)
    denominator = max(active_depth, candidate_depth, 1.0)
    return common / denominator


def _numeric_condition_similarity(active: list[Any], candidate: list[Any]) -> float:
    fields = (
        "weight_on_bit_kn",
        "rotary_rpm",
        "torque_kn_m",
        "rate_of_penetration_m_hr",
        "standpipe_pressure_kpa",
        "flow_rate_lpm",
        "mud_weight_kg_m3",
    )
    active_vals: dict[str, list[float]] = {f: [] for f in fields}
    candidate_vals: dict[str, list[float]] = {f: [] for f in fields}
    for row in active:
        for field in fields:
            value = getattr(row, field, None)
            if value is not None:
                active_vals[field].append(float(value))
    for row in candidate:
        for field in fields:
            value = getattr(row, field, None)
            if value is not None:
                candidate_vals[field].append(float(value))

    scores = []
    for field in fields:
        if not active_vals[field] or not candidate_vals[field]:
            continue
        a, b = mean(active_vals[field]), mean(candidate_vals[field])
        scale = max(abs(a), abs(b), 1e-9)
        scores.append(max(0.0, 1.0 - abs(a - b) / scale))
    return mean(scores) if scores else 0.0


class GeoSpatialEngine:
    """Application service for nearby and offset-well intelligence."""

    def __init__(self, repository: PostGISWellRepository):
        self.repository = repository

    def get_nearby_wells(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        *,
        formation: str | None = None,
        reservoir: str | None = None,
        depth_range: tuple[float, float] | None = None,
        exclude_well_id: str | None = None,
        limit: int = 100,
    ) -> NearbyWellsResponse:
        """Search wells around coordinates and apply optional geological filters."""
        rows = self.repository.nearby(
            latitude, longitude, radius_km,
            formation=formation, reservoir=reservoir,
            depth_range=depth_range,
            exclude_well_id=exclude_well_id, limit=limit,
        )
        result = []
        for well, distance_km in rows:
            forms = self.repository.formations(well.well_id)
            result.append(
                NearbyWell(
                    well_id=well.well_id,
                    well_name=well.well_name,
                    field_name=well.field_name,
                    operator=well.operator,
                    status=well.status,
                    latitude=float(well.latitude),
                    longitude=float(well.longitude),
                    total_depth_m=float(well.total_depth_m) if well.total_depth_m is not None else None,
                    distance_km=round(distance_km, 3),
                    formations=sorted(_formations(forms)),
                    reservoirs=sorted(_reservoirs(well, forms)),
                    depth_overlap_m=(
                        _depth_overlap(float(well.total_depth_m), float(well.total_depth_m), depth_range)
                        if depth_range and well.total_depth_m is not None else None
                    ),
                )
            )
        return NearbyWellsResponse(
            source="active_well" if exclude_well_id else "coordinates",
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            count=len(result),
            wells=result,
        )

    def get_trajectory(self, well_id: str) -> TrajectoryResponse:
        """Return an ordered trajectory suitable for comparison or plotting."""
        points = []
        for row, lon, lat in self.repository.trajectory_with_coordinates(well_id):
            points.append(
                TrajectoryPoint(
                    sequence_no=row.sequence_no,
                    measured_depth_m=float(row.measured_depth_m),
                    tvd_m=float(row.tvd_m) if row.tvd_m is not None else None,
                    inclination_deg=float(row.inclination_deg) if row.inclination_deg is not None else None,
                    azimuth_deg=float(row.azimuth_deg) if row.azimuth_deg is not None else None,
                    latitude=float(lat) if lat is not None else None,
                    longitude=float(lon) if lon is not None else None,
                )
            )
        return TrajectoryResponse(well_id=well_id, points=points)

    def compare_trajectories(self, active_well_id: str, offset_well_id: str) -> TrajectoryComparison:
        """Compare two trajectories over their common measured-depth interval."""
        a = self.repository.trajectory(active_well_id)
        b = self.repository.trajectory(offset_well_id)
        if not a or not b:
            return TrajectoryComparison(
                active_well_id=active_well_id, offset_well_id=offset_well_id,
                common_depth_from_m=None, common_depth_to_m=None,
                common_depth_span_m=0, mean_tvd_difference_m=None,
                max_tvd_difference_m=None, mean_inclination_difference_deg=None,
                comparable_points=0,
            )

        amap = {round(float(p.measured_depth_m), 2): p for p in a if p.tvd_m is not None}
        bmap = {round(float(p.measured_depth_m), 2): p for p in b if p.tvd_m is not None}
        common = sorted(set(amap) & set(bmap))
        if not common:
            a_min, a_max = float(a[0].measured_depth_m), float(a[-1].measured_depth_m)
            b_min, b_max = float(b[0].measured_depth_m), float(b[-1].measured_depth_m)
            start, end = max(a_min, b_min), min(a_max, b_max)
            return TrajectoryComparison(
                active_well_id=active_well_id, offset_well_id=offset_well_id,
                common_depth_from_m=start if start <= end else None,
                common_depth_to_m=end if start <= end else None,
                common_depth_span_m=max(0.0, end-start),
                mean_tvd_difference_m=None, max_tvd_difference_m=None,
                mean_inclination_difference_deg=None, comparable_points=0,
            )

        tvd_diffs = [abs(float(amap[d].tvd_m) - float(bmap[d].tvd_m)) for d in common]
        inc_diffs = [
            abs(float(amap[d].inclination_deg) - float(bmap[d].inclination_deg))
            for d in common
            if amap[d].inclination_deg is not None and bmap[d].inclination_deg is not None
        ]
        return TrajectoryComparison(
            active_well_id=active_well_id,
            offset_well_id=offset_well_id,
            common_depth_from_m=common[0],
            common_depth_to_m=common[-1],
            common_depth_span_m=common[-1] - common[0],
            mean_tvd_difference_m=mean(tvd_diffs),
            max_tvd_difference_m=max(tvd_diffs),
            mean_inclination_difference_deg=mean(inc_diffs) if inc_diffs else None,
            comparable_points=len(common),
        )

    def find_similar_offset_wells(
        self,
        active_well_id: str,
        radius_km: float,
        formation: str | None = None,
        depth_range: tuple[float, float] | None = None,
        *,
        limit: int = 20,
    ) -> SimilarOffsetWellsResponse:
        """Rank nearby wells with an explainable deterministic similarity score.

        The score is a heuristic for decision support, not a trained ML model.
        Weights sum to 100: distance 30, formation 20, reservoir 10,
        depth 15, historical events 15, drilling conditions 10.
        """
        active = self.repository.get_well(active_well_id)
        if active is None:
            raise ValueError(f"Active well not found: {active_well_id}")

        active_forms = self.repository.formations(active_well_id)
        active_form_names = _formations(active_forms)
        active_reservoirs = _reservoirs(active, active_forms)
        active_events = {str(e.event_type) for e in self.repository.events(active_well_id)}
        active_params = self.repository.parameters(active_well_id, depth_range)
        candidates = self.repository.nearby(
            float(active.latitude), float(active.longitude), radius_km,
            formation=formation, depth_range=depth_range,
            exclude_well_id=active_well_id, limit=max(limit * 5, 50),
        )

        ranked: list[SimilarOffsetWell] = []
        for candidate, distance_km in candidates:
            forms = self.repository.formations(candidate.well_id)
            form_names = _formations(forms)
            reservoirs = _reservoirs(candidate, forms)
            events = {str(e.event_type) for e in self.repository.events(candidate.well_id)}
            shared_forms = sorted(active_form_names & form_names)
            shared_reservoirs = sorted(active_reservoirs & reservoirs)
            shared_events = sorted(active_events & events)

            spatial = max(0.0, 1.0 - distance_km / max(radius_km, 1e-9))
            formation_score = len(shared_forms) / max(1, len(active_form_names))
            reservoir_score = len(shared_reservoirs) / max(1, len(active_reservoirs))
            depth_score = _interval_overlap_score(
                float(active.total_depth_m) if active.total_depth_m is not None else None,
                float(candidate.total_depth_m) if candidate.total_depth_m is not None else None,
                depth_range,
            )
            event_score = len(shared_events) / max(1, len(active_events))
            candidate_params = self.repository.parameters(candidate.well_id, depth_range)
            drilling_score = _numeric_condition_similarity(active_params, candidate_params)

            factors = SimilarityFactors(
                spatial_score=round(spatial, 4),
                formation_score=round(formation_score, 4),
                reservoir_score=round(reservoir_score, 4),
                depth_score=round(depth_score, 4),
                event_score=round(event_score, 4),
                drilling_condition_score=round(drilling_score, 4),
            )
            total = (
                spatial * 30 + formation_score * 20 + reservoir_score * 10
                + depth_score * 15 + event_score * 15 + drilling_score * 10
            )
            nearby = NearbyWell(
                well_id=candidate.well_id,
                well_name=candidate.well_name,
                field_name=candidate.field_name,
                operator=candidate.operator,
                status=candidate.status,
                latitude=float(candidate.latitude),
                longitude=float(candidate.longitude),
                total_depth_m=float(candidate.total_depth_m) if candidate.total_depth_m is not None else None,
                distance_km=round(distance_km, 3),
                formations=sorted(form_names),
                reservoirs=sorted(reservoirs),
                depth_overlap_m=_depth_overlap(
                    float(active.total_depth_m) if active.total_depth_m is not None else None,
                    float(candidate.total_depth_m) if candidate.total_depth_m is not None else None,
                    depth_range,
                ),
            )
            ranked.append(SimilarOffsetWell(
                well=nearby,
                similarity_score=round(total, 2),
                factors=factors,
                shared_formations=shared_forms,
                shared_reservoirs=shared_reservoirs,
                shared_events=shared_events,
            ))

        ranked.sort(key=lambda x: (-x.similarity_score, x.well.distance_km))
        return SimilarOffsetWellsResponse(
            active_well_id=active_well_id,
            radius_km=radius_km,
            formation=formation,
            depth_range=DepthRange(from_m=depth_range[0], to_m=depth_range[1]) if depth_range else None,
            count=min(limit, len(ranked)),
            wells=ranked[:limit],
        )

    def nearby_geojson(self, **kwargs: Any) -> dict[str, Any]:
        """Return nearby wells as a Leaflet-compatible GeoJSON FeatureCollection."""
        response = self.get_nearby_wells(**kwargs)
        return wells_to_feature_collection(response)

    def trajectory_geojson(self, well_id: str) -> dict[str, Any]:
        """Return a well trajectory as a GeoJSON LineString FeatureCollection."""
        return trajectories_to_feature_collection(self.repository.trajectory_with_coordinates(well_id), well_id)
