from fastapi import APIRouter, Depends, Query
from ..dependencies import get_prediction_service
from ..schemas import *
from ..services.interfaces import PredictionService

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.get("", response_model=PredictionListResponse, summary="List risk predictions")
def list_predictions(well_id: str | None = None, risk_type: str | None = None, limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), service: PredictionService = Depends(get_prediction_service)):
    items, total = service.list_predictions(well_id, risk_type, limit, offset)
    return PredictionListResponse(items=items, pagination=Pagination(limit=limit, offset=offset, total=total))

@router.post("/risk", response_model=RiskPredictionResponse, summary="Predict drilling risk")
def predict_risk(request: RiskPredictionRequest, service: PredictionService = Depends(get_prediction_service)):
    return service.predict(request.well_id, request.risk_type, request.features)
