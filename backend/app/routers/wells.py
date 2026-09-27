from fastapi import APIRouter, Depends, Query
from ..dependencies import get_well_service
from ..schemas import *
from ..services.interfaces import WellService

router = APIRouter(prefix="/wells", tags=["Wells"])

@router.get("/nearby", response_model=NearbyWellsResponse, summary="Find nearby wells")
def nearby_wells(well_id: str = Query(min_length=1), radius_km: float = Query(default=25, gt=0, le=500), limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), service: WellService = Depends(get_well_service)):
    items, total = service.nearby_wells(well_id, radius_km, limit, offset)
    return NearbyWellsResponse(source_well_id=well_id, radius_km=radius_km, items=items, pagination=Pagination(limit=limit, offset=offset, total=total))

@router.get("", response_model=WellListResponse, summary="List wells")
def list_wells(limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), service: WellService = Depends(get_well_service)):
    items, total = service.list_wells(limit, offset)
    return WellListResponse(items=items, pagination=Pagination(limit=limit, offset=offset, total=total))

@router.get("/{well_id}", response_model=WellResponse, summary="Get a well")
def get_well(well_id: str, service: WellService = Depends(get_well_service)):
    return service.get_well(well_id)

@router.get("/{well_id}/events", response_model=EventListResponse, summary="Get well events")
def get_events(well_id: str, event_type: str | None = Query(default=None), limit: int = Query(default=100, ge=1, le=5000), offset: int = Query(default=0, ge=0), service: WellService = Depends(get_well_service)):
    items, total = service.events(well_id, event_type, limit, offset)
    return EventListResponse(items=items, pagination=Pagination(limit=limit, offset=offset, total=total))

@router.get("/{well_id}/monitoring", response_model=MonitoringSnapshotResponse, summary="Get latest drilling monitoring snapshot")
def get_monitoring(well_id: str, service: WellService = Depends(get_well_service)):
    return service.monitoring(well_id)


@router.get("/{well_id}/trend", response_model=list[TrendPointResponse], summary="Get recent drilling trend")
def get_trend(well_id: str, limit: int = Query(default=120, ge=1, le=1000), service: WellService = Depends(get_well_service)):
    return service.trend(well_id, limit)


@router.get("/{well_id}/trajectory", response_model=TrajectoryResponse, summary="Get well trajectory")
def get_trajectory(well_id: str, limit: int = Query(default=500, ge=1, le=10000), offset: int = Query(default=0, ge=0), service: WellService = Depends(get_well_service)):
    items, _ = service.trajectory(well_id, limit, offset)
    return TrajectoryResponse(well_id=well_id, items=items)
