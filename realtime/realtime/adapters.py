from __future__ import annotations

import asyncio
import random
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from .models import DrillingParameterUpdate


class ERTMACAdapter(ABC):
    """Provider-neutral interface for an eRTMAC real-time source.

    A production OIL eRTMAC implementation should subclass this class and
    implement ``stream`` without changing the downstream validation,
    normalization, WebSocket, or prediction interfaces.
    """

    name = "ertmac"

    @abstractmethod
    async def stream(self, well_id: str, stop_event: asyncio.Event) -> AsyncIterator[DrillingParameterUpdate]:
        """Yield canonical parameter updates until ``stop_event`` is set."""
        raise NotImplementedError

    async def start(self, well_id: str) -> None:
        """Optional lifecycle hook executed before streaming a well."""

    async def stop(self, well_id: str) -> None:
        """Optional lifecycle hook executed after streaming a well."""


class MockERTMACAdapter(ERTMACAdapter):
    """Deterministic, realistic-looking drilling parameter generator.

    The generated values are synthetic and are never presented as OIL data.
    The generator deliberately introduces occasional abnormal samples so
    validation/alerting can be tested without real eRTMAC access.
    """

    name = "mock"

    def __init__(self, interval_seconds: float = 1.0, seed: int = 42) -> None:
        self.interval_seconds = interval_seconds
        self._random = random.Random(seed)
        self._state: dict[str, dict[str, float]] = {}
        self._sequence: dict[str, int] = {}

    def _initial_state(self, well_id: str) -> dict[str, float]:
        if well_id not in self._state:
            self._state[well_id] = {
                "depth": 2400.0 + self._random.uniform(0, 250),
                "rop": self._random.uniform(4.0, 8.0),
                "wob": self._random.uniform(12.0, 28.0),
                "rpm": self._random.uniform(70.0, 120.0),
                "torque": self._random.uniform(35.0, 70.0),
                "pressure": self._random.uniform(250.0, 340.0),
                "mud_flow": self._random.uniform(150.0, 230.0),
                "mud_weight": self._random.uniform(9.5, 11.5),
            }
        return self._state[well_id]

    def _next(self, well_id: str) -> DrillingParameterUpdate:
        state = self._initial_state(well_id)
        # Slow random walk produces plausible continuity between samples.
        state["depth"] += max(0.05, state["rop"] / 60.0 + self._random.uniform(-0.02, 0.03))
        state["rop"] = max(0.1, state["rop"] + self._random.uniform(-0.35, 0.35))
        state["wob"] = max(1.0, state["wob"] + self._random.uniform(-1.2, 1.2))
        state["rpm"] = max(5.0, state["rpm"] + self._random.uniform(-3.0, 3.0))
        state["torque"] = max(1.0, state["torque"] + self._random.uniform(-3.0, 3.0))
        state["pressure"] = max(10.0, state["pressure"] + self._random.uniform(-6.0, 6.0))
        state["mud_flow"] = max(1.0, state["mud_flow"] + self._random.uniform(-5.0, 5.0))
        state["mud_weight"] = max(1.0, state["mud_weight"] + self._random.uniform(-0.04, 0.04))

        sequence = self._sequence.get(well_id, 0) + 1
        self._sequence[well_id] = sequence

        # Every 25th sample is intentionally abnormal for pipeline testing.
        if sequence % 25 == 0:
            state["torque"] *= 1.9
            state["pressure"] *= 1.45

        return DrillingParameterUpdate(
            well_id=well_id,
            timestamp=datetime.now(timezone.utc),
            sequence=sequence,
            source="mock_ertmac_synthetic",
            **{key: round(value, 3) for key, value in state.items()},
        )

    async def stream(self, well_id: str, stop_event: asyncio.Event) -> AsyncIterator[DrillingParameterUpdate]:
        """Generate updates until the stream is stopped or cancelled."""
        while not stop_event.is_set():
            yield self._next(well_id)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=self.interval_seconds)
            except asyncio.TimeoutError:
                continue
