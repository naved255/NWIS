from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4
from .interfaces import WellService, KnowledgeService, PredictionService, AlertService, RecommendationService, RealtimeService
from ..errors import ResourceNotFound
from ..schemas import *

_NOW = datetime.now(timezone.utc)


class MockWellService(WellService):
    """Deterministic sample service for local development and integration testing."""
    def __init__(self) -> None:
        self.wells = [
            WellResponse(id="w-001", well_id="WELL-001", well_name="Sample Well A", field_name="DEMO-FIELD", block_name="BLOCK-A", operator="SAMPLE", status="DRILLING", latitude=Decimal("28.6139"), longitude=Decimal("77.2090"), total_depth_m=Decimal("3200"), metadata={"sample": True}),
            WellResponse(id="w-002", well_id="WELL-002", well_name="Sample Well B", field_name="DEMO-FIELD", block_name="BLOCK-A", operator="SAMPLE", status="COMPLETED", latitude=Decimal("28.6200"), longitude=Decimal("77.2150"), total_depth_m=Decimal("3100"), metadata={"sample": True}),
        ]

    def list_wells(self, limit: int, offset: int):
        return self.wells[offset:offset+limit], len(self.wells)

    def get_well(self, well_id: str):
        for w in self.wells:
            if w.well_id == well_id:
                return w
        raise ResourceNotFound(f"Well '{well_id}' was not found")

    def nearby_wells(self, well_id: str, radius_km: float, limit: int, offset: int):
        self.get_well(well_id)
        items = [NearbyWellResponse.model_validate({**w.model_dump(), "distance_km": 0.84, "formation_matches": ["F1"], "event_types": ["mud_loss"]}) for w in self.wells if w.well_id != well_id]
        return items[offset:offset+limit], len(items)

    def events(self, well_id: str, event_type: str | None, limit: int, offset: int):
        self.get_well(well_id)
        items = [DrillingEventResponse(id="event-001", well_id=well_id, event_type=event_type or "drilling_anomaly", event_time=_NOW, depth_m=Decimal("2800"), severity="medium", description="Mock/sample event; replace with database service.", duration_min=Decimal("30"), metadata={"sample": True})]
        return items[offset:offset+limit], len(items)

    def trajectory(self, well_id: str, limit: int, offset: int):
        self.get_well(well_id)
        items = [TrajectoryPointResponse(id=f"tp-{i}", well_id=well_id, measured_depth_m=Decimal(str(i * 100)), inclination_deg=Decimal("5"), azimuth_deg=Decimal("90"), tvd_m=Decimal(str(i * 99)), northing_m=Decimal(str(i * 10)), easting_m=Decimal(str(i * 5)), sequence_no=i, metadata={"sample": True}) for i in range(1, 6)]
        return items[offset:offset+limit], len(items)


    def monitoring(self, well_id: str):
        self.get_well(well_id)
        from ..schemas import MonitoringSnapshotResponse
        return MonitoringSnapshotResponse(well_id=well_id, timestamp=_NOW, depth=2800, rop=6.5, wob=24, rpm=95, torque=78, pressure=350, mud_flow=200, mud_weight=10.5, formation="F1")

    def trend(self, well_id: str, limit: int = 120):
        self.get_well(well_id)
        from ..schemas import TrendPointResponse
        return [TrendPointResponse(timestamp=_NOW, depth=2700 + i * 10, rop=5 + (i % 5) * 0.5, torque=60 + (i % 7) * 3, pressure=320 + (i % 6) * 5) for i in range(min(limit, 20))]


class MockKnowledgeService(KnowledgeService):
    def documents(self, well_id, document_type, limit, offset):
        items = [DocumentResponse(id="doc-001", document_id="DOC-001", well_id=well_id or "WELL-001", document_type=document_type or "DDR", title="Sample Daily Drilling Report", storage_key="mock/DOC-001.pdf", mime_type="application/pdf", page_count=5, metadata={"sample": True})]
        return items[offset:offset+limit], len(items)

    def search(self, query, filters, limit):
        return [SearchResult(result_id="chunk-001", score=0.91, title="Sample drilling report", text=f"Mock result for query: {query}", source_uri="mock://DOC-001", document_id="DOC-001", well_id=filters.get("well_id") or "WELL-001", page=1, metadata={"sample": True})][:limit]

    def answer(self, question, filters, include_sources):
        sources = self.search(question, filters, 3)
        return (f"Mock RAG answer for: {question}. Replace MockKnowledgeService with the RAG adapter during integration.", sources if include_sources else [])


class MockPredictionService(PredictionService):
    def __init__(self) -> None:
        self.items: list[RiskPredictionResponse] = []

    def predict(self, well_id, risk_type, features):
        risk = risk_type or "drilling_anomaly"
        probability = 0.72
        response = RiskPredictionResponse(prediction_id=str(uuid4()), well_id=well_id, risk_type=risk, probability=probability, severity="high", confidence=0.78, model_version="mock-1.0.0", explanation={"mode": "mock", "top_features": []}, predicted_at=datetime.now(timezone.utc))
        self.items.insert(0, response)
        return response

    def list_predictions(self, well_id, risk_type, limit, offset):
        items = [p for p in self.items if (well_id is None or p.well_id == well_id) and (risk_type is None or p.risk_type == risk_type)]
        return items[offset:offset+limit], len(items)


class MockAlertService(AlertService):
    def list_alerts(self, well_id, status, limit, offset):
        items = [AlertResponse(id="alert-001", well_id=well_id or "WELL-001", prediction_id=None, alert_type="drilling_anomaly", severity="high", status=status or "OPEN", message="Mock/sample alert.", triggered_at=_NOW, metadata={"sample": True})]
        return items[offset:offset+limit], len(items)


class MockRecommendationService(RecommendationService):
    def list_recommendations(self, well_id, status, limit, offset):
        items = [RecommendationResponse(id="rec-001", well_id=well_id or "WELL-001", prediction_id=None, recommendation_type="monitoring", priority="high", title="Increase monitoring", description="Mock/sample recommendation.", rationale="Replace with the recommendation service implementation.", status=status or "NEW", metadata={"sample": True})]
        return items[offset:offset+limit], len(items)


class MockRealtimeService(RealtimeService):
    def status(self):
        return {"status": "offline", "source": "mock", "last_event_at": None, "message": "Realtime adapter not connected; this is sample mode."}

    async def stream(self, websocket):
        await websocket.accept()
        await websocket.send_json({"type": "status", "data": self.status()})
        await websocket.close()
