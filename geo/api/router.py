"""FastAPI router for NWIS geo-spatial intelligence."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.db import get_session
from ..models.schemas import DepthRange
from ..repositories.postgis import PostGISWellRepository
from ..services.engine import GeoSpatialEngine


router = APIRouter(prefix="/api/v1/geo", tags=["geo-spatial"])


def get_engine(session: Session = Depends(get_session)) -> GeoSpatialEngine:
    """Build the geo-spatial service from the shared NWIS DB session."""
    return GeoSpatialEngine(PostGISWellRepository(session))


@router.get("/nearby", summary="Find wells near coordinates")
def nearby_wells(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(..., gt=0, le=500),
    formation: str | None = None,
    reservoir: str | None = None,
    depth_from_m: float | None = Query(None, ge=0),
    depth_to_m: float | None = Query(None, gt=0),
    limit: int = Query(100, ge=1, le=500),
    engine: GeoSpatialEngine = Depends(get_engine),
):
    """Return nearby wells with optional formation/reservoir/depth filters."""
    depth = None
    if depth_from_m is not None or depth_to_m is not None:
        if depth_from_m is None or depth_to_m is None:
            raise HTTPException(400, "depth_from_m and depth_to_m must be supplied together")
        depth = (depth_from_m, depth_to_m)
    return engine.get_nearby_wells(
        latitude, longitude, radius_km,
        formation=formation, reservoir=reservoir,
        depth_range=depth, limit=limit,
    ).model_dump()


@router.get("/nearby/geojson", summary="Find wells near coordinates as GeoJSON")
def nearby_wells_geojson(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(..., gt=0, le=500),
    formation: str | None = None,
    reservoir: str | None = None,
    depth_from_m: float | None = Query(None, ge=0),
    depth_to_m: float | None = Query(None, gt=0),
    limit: int = Query(100, ge=1, le=500),
    engine: GeoSpatialEngine = Depends(get_engine),
):
    """Return Leaflet-compatible GeoJSON points."""
    depth = None
    if (depth_from_m is None) != (depth_to_m is None):
        raise HTTPException(400, "depth_from_m and depth_to_m must be supplied together")
    if depth_from_m is not None:
        depth = (depth_from_m, depth_to_m)
    return engine.nearby_geojson(
        latitude=latitude, longitude=longitude, radius_km=radius_km,
        formation=formation, reservoir=reservoir, depth_range=depth, limit=limit,
    )


@router.get("/wells/{well_id}/trajectory", summary="Get a well trajectory")
def well_trajectory(well_id: str, engine: GeoSpatialEngine = Depends(get_engine)):
    """Return ordered trajectory points."""
    response = engine.get_trajectory(well_id)
    if not response.points:
        raise HTTPException(404, f"Well or trajectory not found: {well_id}")
    return response.model_dump()


@router.get("/wells/{well_id}/trajectory/geojson", summary="Get trajectory GeoJSON")
def well_trajectory_geojson(well_id: str, engine: GeoSpatialEngine = Depends(get_engine)):
    """Return trajectory as a Leaflet-compatible LineString."""
    response = engine.get_trajectory(well_id)
    if not response.points:
        raise HTTPException(404, f"Well or trajectory not found: {well_id}")
    return engine.trajectory_geojson(well_id)


@router.get("/wells/{active_well_id}/offsets/similar", summary="Rank similar offset wells")
def similar_offset_wells(
    active_well_id: str,
    radius_km: float = Query(25, gt=0, le=500),
    formation: str | None = None,
    depth_from_m: float | None = Query(None, ge=0),
    depth_to_m: float | None = Query(None, gt=0),
    limit: int = Query(20, ge=1, le=100),
    engine: GeoSpatialEngine = Depends(get_engine),
):
    """Return explainable similarity-ranked offset wells."""
    if (depth_from_m is None) != (depth_to_m is None):
        raise HTTPException(400, "depth_from_m and depth_to_m must be supplied together")
    depth = (depth_from_m, depth_to_m) if depth_from_m is not None else None
    try:
        response = engine.find_similar_offset_wells(
            active_well_id, radius_km, formation=formation,
            depth_range=depth, limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return response.model_dump()


@router.get("/wells/{active_well_id}/offsets/similar/geojson", summary="Similar offsets as GeoJSON")
def similar_offset_wells_geojson(
    active_well_id: str,
    radius_km: float = Query(25, gt=0, le=500),
    formation: str | None = None,
    depth_from_m: float | None = Query(None, ge=0),
    depth_to_m: float | None = Query(None, gt=0),
    limit: int = Query(20, ge=1, le=100),
    engine: GeoSpatialEngine = Depends(get_engine),
):
    """Return similarity-ranked offsets in map-ready GeoJSON."""
    if (depth_from_m is None) != (depth_to_m is None):
        raise HTTPException(400, "depth_from_m and depth_to_m must be supplied together")
    depth = (depth_from_m, depth_to_m) if depth_from_m is not None else None
    try:
        response = engine.find_similar_offset_wells(
            active_well_id, radius_km, formation=formation,
            depth_range=depth, limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

    from ..services.geojson import similar_offsets_to_feature_collection
    return similar_offsets_to_feature_collection(response)


@router.get("/wells/{active_well_id}/trajectory-compare/{offset_well_id}", summary="Compare trajectories")
def compare_trajectories(
    active_well_id: str,
    offset_well_id: str,
    engine: GeoSpatialEngine = Depends(get_engine),
):
    """Compare active and offset well trajectories."""
    if engine.repository.get_well(active_well_id) is None:
        raise HTTPException(404, f"Well not found: {active_well_id}")
    if engine.repository.get_well(offset_well_id) is None:
        raise HTTPException(404, f"Well not found: {offset_well_id}")
    return engine.compare_trajectories(active_well_id, offset_well_id).model_dump()
