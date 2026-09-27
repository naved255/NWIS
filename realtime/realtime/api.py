from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError

from .adapters import ERTMACAdapter
from .config import RealtimeSettings
from .manager import RealtimeStreamManager
from .models import StreamCommand, StreamStatus
from .normalizer import normalize_update
from .pipeline import RealtimePipeline
from .prediction import NoopPredictionService, PredictionServiceAdapter

logger = logging.getLogger(__name__)


def build_router(
    adapter: ERTMACAdapter,
    prediction_service: PredictionServiceAdapter | None = None,
    *,
    settings: RealtimeSettings | None = None,
) -> APIRouter:
    """Build an isolated FastAPI router for NWIS real-time streams."""
    settings = settings or RealtimeSettings()
    prediction_service = prediction_service or NoopPredictionService()
    pipeline = RealtimePipeline(prediction_callback=prediction_service.predict)
    manager = RealtimeStreamManager(adapter=adapter, pipeline=pipeline)
    router = APIRouter(tags=["Realtime"])

    @router.get("/realtime/status/{well_id}", response_model=StreamStatus)
    async def stream_status(well_id: str) -> StreamStatus:
        """Return the running state of one well's real-time stream."""
        return StreamStatus(
            well_id=well_id,
            running=manager.is_running(well_id),
            adapter=adapter.name,
            message="stream running" if manager.is_running(well_id) else "stream stopped",
        )

    @router.post("/realtime/{well_id}/start", response_model=StreamStatus)
    async def start_stream(well_id: str) -> StreamStatus:
        """Start a provider stream for a well."""
        await manager.start(well_id)
        return StreamStatus(well_id=well_id, running=True, adapter=adapter.name, message="stream started")

    @router.post("/realtime/{well_id}/stop", response_model=StreamStatus)
    async def stop_stream(well_id: str) -> StreamStatus:
        """Stop a provider stream for a well."""
        await manager.stop(well_id)
        return StreamStatus(well_id=well_id, running=False, adapter=adapter.name, message="stream stopped")

    @router.websocket("/ws/realtime/{well_id}")
    async def realtime_websocket(websocket: WebSocket, well_id: str) -> None:
        """Stream normalized drilling updates for a well over WebSocket.

        Client commands:
        - ``{"action":"start"}`` starts/keeps the provider stream running.
        - ``{"action":"stop"}`` stops it and closes this subscription.
        - ``{"action":"ping"}`` returns a pong.
        - A provider payload can also be supplied as JSON and is normalized and
          processed immediately; this is useful for testing a real adapter.
        """
        await websocket.accept()
        queue = await manager.subscribe(well_id)
        sender = asyncio.create_task(_sender(websocket, queue))
        try:
            await websocket.send_json({
                "event_type": "stream_status",
                "well_id": well_id,
                "running": True,
                "adapter": adapter.name,
                "synthetic": adapter.name == "mock",
            })
            while True:
                message = await websocket.receive_json()
                try:
                    command = StreamCommand.model_validate(message)
                except ValidationError:
                    # Treat non-command JSON as a test/provider payload.
                    update = normalize_update(message, well_id=well_id)
                    event = await pipeline.process(update)
                    await websocket.send_json(event.model_dump(mode="json"))
                    continue

                if command.action == "ping":
                    await websocket.send_json({"event_type": "pong", "well_id": well_id})
                elif command.action == "start":
                    await manager.start(well_id)
                    await websocket.send_json({"event_type": "stream_status", "well_id": well_id, "running": True})
                elif command.action == "stop":
                    await manager.stop(well_id)
                    await websocket.send_json({"event_type": "stream_status", "well_id": well_id, "running": False})
                    break
        except WebSocketDisconnect:
            logger.info("Realtime WebSocket disconnected well_id=%s", well_id)
        finally:
            sender.cancel()
            try:
                await sender
            except asyncio.CancelledError:
                pass
            await manager.unsubscribe(well_id, queue)

    return router


async def _sender(websocket: WebSocket, queue: asyncio.Queue) -> None:
    while True:
        event = await queue.get()
        await websocket.send_json(event.model_dump(mode="json"))
