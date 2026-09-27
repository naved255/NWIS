from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from ..schemas import (
    AlertResponse, DocumentResponse, NearbyWellResponse, RecommendationResponse,
    RiskPredictionResponse, SearchResult, TrajectoryPointResponse, DrillingEventResponse,
    WellResponse,
)


class WellService(ABC):
    @abstractmethod
    def list_wells(self, limit: int, offset: int) -> tuple[list[WellResponse], int]: ...

    @abstractmethod
    def get_well(self, well_id: str) -> WellResponse: ...

    @abstractmethod
    def nearby_wells(self, well_id: str, radius_km: float, limit: int, offset: int) -> tuple[list[NearbyWellResponse], int]: ...

    @abstractmethod
    def events(self, well_id: str, event_type: str | None, limit: int, offset: int) -> tuple[list[DrillingEventResponse], int]: ...

    @abstractmethod
    def trajectory(self, well_id: str, limit: int, offset: int) -> tuple[list[TrajectoryPointResponse], int]: ...

    @abstractmethod
    def monitoring(self, well_id: str) -> Any: ...

    @abstractmethod
    def trend(self, well_id: str, limit: int = 120) -> list[Any]: ...


class KnowledgeService(ABC):
    @abstractmethod
    def documents(self, well_id: str | None, document_type: str | None, limit: int, offset: int) -> tuple[list[DocumentResponse], int]: ...

    @abstractmethod
    def search(self, query: str, filters: dict[str, Any], limit: int) -> list[SearchResult]: ...

    @abstractmethod
    def answer(self, question: str, filters: dict[str, Any], include_sources: bool) -> tuple[str, list[SearchResult]]: ...


class PredictionService(ABC):
    @abstractmethod
    def predict(self, well_id: str | None, risk_type: str | None, features: dict[str, Any]) -> RiskPredictionResponse: ...

    @abstractmethod
    def list_predictions(self, well_id: str | None, risk_type: str | None, limit: int, offset: int) -> tuple[list[RiskPredictionResponse], int]: ...


class AlertService(ABC):
    @abstractmethod
    def list_alerts(self, well_id: str | None, status: str | None, limit: int, offset: int) -> tuple[list[AlertResponse], int]: ...


class RecommendationService(ABC):
    @abstractmethod
    def list_recommendations(self, well_id: str | None, status: str | None, limit: int, offset: int) -> tuple[list[RecommendationResponse], int]: ...


class RealtimeService(ABC):
    @abstractmethod
    def status(self) -> dict[str, Any]: ...

    @abstractmethod
    async def stream(self, websocket: Any) -> None: ...
