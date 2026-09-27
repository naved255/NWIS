from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .models import DrillingParameterUpdate


class PredictionServiceAdapter(ABC):
    """Small interface for forwarding real-time samples to NWIS prediction."""

    @abstractmethod
    async def predict(self, update: DrillingParameterUpdate) -> Any:
        """Send one normalized sample to the prediction service."""
        raise NotImplementedError


class NoopPredictionService(PredictionServiceAdapter):
    """Safe development adapter used when the ML service is unavailable."""

    async def predict(self, update: DrillingParameterUpdate) -> None:
        return None
