from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

from .adapters import ERTMACAdapter
from .models import NormalizedRealtimeEvent
from .pipeline import RealtimePipeline

logger = logging.getLogger(__name__)


@dataclass
class ActiveStream:
    well_id: str
    stop_event: asyncio.Event
    task: asyncio.Task | None = None
    subscribers: set[asyncio.Queue[NormalizedRealtimeEvent]] = field(default_factory=set)


class RealtimeStreamManager:
    """Coordinates adapter streams and WebSocket subscribers per well."""

    def __init__(self, adapter: ERTMACAdapter, pipeline: RealtimePipeline) -> None:
        self.adapter = adapter
        self.pipeline = pipeline
        self._streams: dict[str, ActiveStream] = {}
        self._lock = asyncio.Lock()

    async def start(self, well_id: str) -> ActiveStream:
        async with self._lock:
            stream = self._streams.get(well_id)
            if stream and stream.task and not stream.task.done():
                return stream
            stream = ActiveStream(well_id=well_id, stop_event=asyncio.Event())
            stream.task = asyncio.create_task(self._run(stream), name=f"nwis-realtime-{well_id}")
            self._streams[well_id] = stream
            return stream

    async def stop(self, well_id: str) -> None:
        async with self._lock:
            stream = self._streams.get(well_id)
            if not stream:
                return
            stream.stop_event.set()
        if stream.task:
            try:
                await stream.task
            except asyncio.CancelledError:
                pass

    async def subscribe(self, well_id: str) -> asyncio.Queue[NormalizedRealtimeEvent]:
        stream = await self.start(well_id)
        queue: asyncio.Queue[NormalizedRealtimeEvent] = asyncio.Queue(maxsize=50)
        stream.subscribers.add(queue)
        return queue

    async def unsubscribe(self, well_id: str, queue: asyncio.Queue[NormalizedRealtimeEvent]) -> None:
        stream = self._streams.get(well_id)
        if not stream:
            return
        stream.subscribers.discard(queue)

    def is_running(self, well_id: str) -> bool:
        stream = self._streams.get(well_id)
        return bool(stream and stream.task and not stream.task.done())

    async def _run(self, stream: ActiveStream) -> None:
        try:
            await self.adapter.start(stream.well_id)
            async for update in self.adapter.stream(stream.well_id, stream.stop_event):
                event = await self.pipeline.process(update)
                dead: list[asyncio.Queue] = []
                for queue in stream.subscribers:
                    try:
                        queue.put_nowait(event)
                    except asyncio.QueueFull:
                        dead.append(queue)
                for queue in dead:
                    stream.subscribers.discard(queue)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Real-time adapter failed well_id=%s", stream.well_id)
        finally:
            try:
                await self.adapter.stop(stream.well_id)
            except Exception:
                logger.exception("Real-time adapter stop failed well_id=%s", stream.well_id)
            async with self._lock:
                current = self._streams.get(stream.well_id)
                if current is stream:
                    self._streams.pop(stream.well_id, None)
