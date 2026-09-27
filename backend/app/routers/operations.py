from fastapi import APIRouter, Depends, Query
from ..dependencies import get_alert_service, get_recommendation_service
from ..schemas import *
from ..services.interfaces import AlertService, RecommendationService

router = APIRouter(tags=["Operations"])

@router.get("/alerts", response_model=AlertListResponse, summary="List operational alerts")
def alerts(well_id: str | None = None, status: str | None = None, limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), service: AlertService = Depends(get_alert_service)):
    items, total = service.list_alerts(well_id, status, limit, offset)
    return AlertListResponse(items=items, pagination=Pagination(limit=limit, offset=offset, total=total))

@router.get("/recommendations", response_model=RecommendationListResponse, summary="List operational recommendations")
def recommendations(well_id: str | None = None, status: str | None = None, limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), service: RecommendationService = Depends(get_recommendation_service)):
    items, total = service.list_recommendations(well_id, status, limit, offset)
    return RecommendationListResponse(items=items, pagination=Pagination(limit=limit, offset=offset, total=total))
