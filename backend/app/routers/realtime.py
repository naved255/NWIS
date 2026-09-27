from fastapi import APIRouter, Depends, WebSocket
from ..dependencies import get_realtime_service
from ..schemas import RealtimeStatusResponse
from ..services.interfaces import RealtimeService

router = APIRouter(prefix="/realtime", tags=["Realtime"])

@router.get("/status", response_model=RealtimeStatusResponse, summary="Get realtime source status")
def realtime_status(service: RealtimeService = Depends(get_realtime_service)):
    return service.status()

@router.websocket("/ws")
async def realtime_ws(websocket: WebSocket):
    service = get_realtime_service()
    await service.stream(websocket)
