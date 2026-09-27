"""Pydantic contracts for the NWIS geo-spatial module."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class CoordinateQuery(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_km: float = Field(gt=0, le=500)


class DepthRange(BaseModel):
    from_m: float = Field(ge=0)
    to_m: float = Field(gt=0)

    def normalized(self) -> tuple[float, float]:
        if self.from_m > self.to_m:
            return self.to_m, self.from_m
        return self.from_m, self.to_m


class NearbyWell(BaseModel):
    well_id: str
    well_name: str | None = None
    field_name: str | None = None
    operator: str | None = None
    status: str | None = None
    latitude: float
    longitude: float
    total_depth_m: float | None = None
    distance_km: float
    formations: list[str] = Field(default_factory=list)
    reservoirs: list[str] = Field(default_factory=list)
    depth_overlap_m: float | None = None


class NearbyWellsResponse(BaseModel):
    source: Literal["coordinates", "active_well"] = "coordinates"
    latitude: float
    longitude: float
    radius_km: float
    count: int
    wells: list[NearbyWell]


class TrajectoryPoint(BaseModel):
    sequence_no: int
    measured_depth_m: float
    tvd_m: float | None = None
    inclination_deg: float | None = None
    azimuth_deg: float | None = None
    latitude: float | None = None
    longitude: float | None = None


class TrajectoryResponse(BaseModel):
    well_id: str
    points: list[TrajectoryPoint]


class TrajectoryComparison(BaseModel):
    active_well_id: str
    offset_well_id: str
    common_depth_from_m: float | None
    common_depth_to_m: float | None
    common_depth_span_m: float
    mean_tvd_difference_m: float | None
    max_tvd_difference_m: float | None
    mean_inclination_difference_deg: float | None
    comparable_points: int


class SimilarityFactors(BaseModel):
    spatial_score: float
    formation_score: float
    reservoir_score: float
    depth_score: float
    event_score: float
    drilling_condition_score: float


class SimilarOffsetWell(BaseModel):
    well: NearbyWell
    similarity_score: float = Field(ge=0, le=100)
    factors: SimilarityFactors
    shared_formations: list[str] = Field(default_factory=list)
    shared_reservoirs: list[str] = Field(default_factory=list)
    shared_events: list[str] = Field(default_factory=list)


class SimilarOffsetWellsResponse(BaseModel):
    active_well_id: str
    radius_km: float
    formation: str | None
    depth_range: DepthRange | None
    count: int
    wells: list[SimilarOffsetWell]


class GeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: dict[str, Any]
    properties: dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoJSONFeature]
    metadata: dict[str, Any] = Field(default_factory=dict)


class GeoJSONTrajectoryFeatureCollection(GeoJSONFeatureCollection):
    pass

