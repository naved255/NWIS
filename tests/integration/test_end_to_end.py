
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from document_intelligence import DocumentIntelligencePipeline
from document_intelligence.ocr.base import OCRAdapter
from ingestion.models.entities import Well as IngestWell, DrillingEvent as IngestEvent
from ingestion.models.entities import SourceMetadata
from nlp_extraction import DrillingNLPExtractor
from nlp_extraction.models import DocumentInput, DocumentPage
from rag.nwis_rag.schemas import RetrievalFilters, EvidenceItem as RAGEvidenceItem
from rag.nwis_rag.service import RAGService
from geo.services.engine import GeoSpatialEngine
from ml.risk_engine.engine import RiskPredictionEngine
from ml.risk_engine.features import engineer_features
from ml.risk_engine.schemas import TrainingConfig
from realtime.models import DrillingParameterUpdate
from realtime.pipeline import RealtimePipeline
from realtime.validator import ParameterLimits
from nwis_decision_support.explainability.service import explain_prediction
from nwis_decision_support.alerts.models import AlertContext, AlertRule, HistoricalEvidence, ParameterAnomaly
from nwis_decision_support.alerts.service import generate_alert
from nwis_decision_support.recommendations.models import EvidenceItem, RecommendationContext
from nwis_decision_support.recommendations.service import generate_recommendation


class FakeOCR(OCRAdapter):
    def extract_text(self, image):
        return "At 2920 m severe mud loss occurred while drilling through the F3 Formation. Mitigation: reduced pump rate."


class FakeVectorStore:
    def __init__(self, evidence):
        self.evidence = evidence

    def similarity_search(self, query, *, filters=None, k=8, score_threshold=None):
        rows = self.evidence
        if filters and filters.well_id:
            rows = [x for x in rows if x.metadata.get("well_id") == filters.well_id]
        if filters and filters.event_type:
            rows = [x for x in rows if x.metadata.get("event_type") == filters.event_type]
        return rows[:k]


class FakeGeoRepo:
    def __init__(self):
        self.active = SimpleNamespace(
            id="db-001", well_id="WELL-001", well_name="Active",
            field_name="FIELD", operator="OIL", status="DRILLING",
            latitude=27.5, longitude=95.2, total_depth_m=3000,
            metadata_json={"formation": "F3"},
        )
        self.offset = SimpleNamespace(
            id="db-002", well_id="WELL-002", well_name="Offset",
            field_name="FIELD", operator="OIL", status="COMPLETED",
            latitude=27.53, longitude=95.22, total_depth_m=3050,
            metadata_json={"formation": "F3"},
        )

    def get_well(self, well_id):
        return {"WELL-001": self.active, "WELL-002": self.offset}.get(well_id)

    def nearby(self, *args, **kwargs):
        return [(self.offset, 3.8)] if kwargs.get("exclude_well_id") == "WELL-001" else [(self.active, 0.0), (self.offset, 3.8)]

    def formations(self, well_id):
        return [SimpleNamespace(formation_name="F3", properties={"reservoir": "R1"})]

    def events(self, well_id, limit=500):
        return [SimpleNamespace(event_type="MUD_LOSS")]

    def parameters(self, well_id, depth_range=None, limit=5000):
        return [SimpleNamespace(weight_on_bit_kn=90, rotary_rpm=120, torque_kn_m=8,
                                rate_of_penetration_m_hr=18, standpipe_pressure_kpa=12000,
                                flow_rate_lpm=1800, mud_weight_kg_m3=1180)]

    def trajectory(self, well_id):
        return [
            SimpleNamespace(measured_depth_m=0, tvd_m=0, inclination_deg=0, sequence_no=0),
            SimpleNamespace(measured_depth_m=1500, tvd_m=1490, inclination_deg=2.5, sequence_no=1),
        ]

    def trajectory_with_coordinates(self, well_id):
        return [
            (SimpleNamespace(measured_depth_m=0), 95.2, 27.5),
            (SimpleNamespace(measured_depth_m=1500), 95.2, 27.5),
        ]


def test_complete_historical_intelligence_pipeline(tmp_path):
    # Historical document -> OCR -> structured document.
    import fitz
    pdf_path = tmp_path / "DDR-WELL-001.pdf"
    pdf = fitz.open()
    pdf.new_page(width=300, height=200)
    pdf.save(pdf_path)
    pdf.close()
    document = DocumentIntelligencePipeline(ocr_adapter=FakeOCR(), min_native_chars=20).process(
        pdf_path, document_id="DOC-001", document_type="DDR"
    )
    assert document.pages[0].text_extraction_method == "ocr"

    # OCR output -> NLP extraction.
    nlp_input = DocumentInput(
        document_id=document.document_id,
        pages=[DocumentPage(page_number=p.page_number, text=p.text) for p in document.pages],
        metadata={"well_id": "WELL-001"},
    )
    extracted = DrillingNLPExtractor().extract(nlp_input)
    assert extracted.events
    assert extracted.events[0].event_type.value == "MUD_LOSS"
    assert extracted.events[0].depth_m == 2920

    # NLP -> canonical DB-compatible entities.
    source = SourceMetadata(source_type="pdf", source_name=document.file_name, source_record_id=document.document_id)
    well = IngestWell(well_id="WELL-001", well_name="Active", source_metadata=source)
    event = IngestEvent(
        event_id="EV-001", well_id=well.well_id, event_type=extracted.events[0].event_type.value,
        depth=extracted.events[0].depth_m, severity=extracted.events[0].severity.value,
        description=extracted.events[0].description, source_metadata=source,
    )
    assert well.well_id == event.well_id == "WELL-001"

    # NLP -> vector-store contract -> RAG.
    evidence = RAGEvidenceItem(
        evidence_id="chunk-001", text=extracted.events[0].description,
        score=0.92, source_uri="document://DOC-001", source_name=document.file_name,
        page=1, metadata={"well_id": "WELL-001", "event_type": "mud_loss", "depth": 2920},
    )
    rag = RAGService(store=FakeVectorStore([evidence]))
    retrieval = rag.retrieve_similar_documents("mud loss at 2920 m", filters=RetrievalFilters(well_id="WELL-001"), top_k=3)
    assert retrieval.sufficient_evidence
    assert retrieval.evidence[0].evidence_id == "chunk-001"

    # Nearby wells / GeoJSON.
    geo = GeoSpatialEngine(FakeGeoRepo())
    nearby = geo.get_nearby_wells(27.5, 95.2, 10)
    assert nearby.count == 2
    geojson = geo.nearby_geojson(latitude=27.5, longitude=95.2, radius_km=10)
    assert geojson["type"] == "FeatureCollection"
    assert geojson["features"][1]["geometry"]["type"] == "Point"

    # ML prediction on the same canonical drilling feature vocabulary.
    df = pd.read_csv(Path("ml/examples/sample_training_data.csv"))
    df = pd.concat([
        df.assign(timestamp=lambda x: pd.to_datetime(x.timestamp) + pd.to_timedelta(i * 12, unit="h"))
        for i in range(8)
    ], ignore_index=True)
    artifact_dir = tmp_path / "risk-artifact"
    engine = RiskPredictionEngine(str(artifact_dir), "integration-1.0")
    engine.fit(df, "stuck_pipe", TrainingConfig(n_estimators=20))
    raw_features = df.iloc[6].drop("risk_type").to_dict()
    prediction = engine.predict_risk(raw_features)
    assert 0 <= prediction.probability <= 1

    # SHAP explains the exact engineered model input.
    model_input = engineer_features(pd.DataFrame([raw_features])).iloc[0].to_dict()
    explanation = explain_prediction(
        engine.pipeline, model_input, "stuck_pipe",
        probability=prediction.probability, prediction_id="P-001", well_id="WELL-001"
    )
    assert explanation.features
    assert explanation.prediction_id == "P-001"

    # Alert consumes ML + historical evidence + active depth.
    alert_context = AlertContext(
        well_id="WELL-001", risk_type="stuck_pipe",
        probability=max(prediction.probability, 0.76), severity="high",
        depth_m=2920, risk_interval_start_m=2900, risk_interval_end_m=3000,
        historical_evidence=[HistoricalEvidence(
            well_id="WELL-002", event_type="stuck_pipe", similarity=0.88,
            depth_start_m=2900, depth_end_m=3000, formation="F3", source_id="EV-OFFSET"
        )],
        parameter_anomalies=[ParameterAnomaly(parameter="torque", value=90, baseline=60, anomaly_score=0.9)],
    )
    alert = generate_alert(alert_context, rules=[AlertRule(
        name="integration-risk", min_probability=0.75,
        require_historical_match=True, min_historical_similarity=0.7,
        require_depth_in_interval=True, require_parameter_anomaly=False,
    )])
    assert alert.generated
    assert alert.evidence

    # Alert/RAG evidence -> recommendation.
    rec = generate_recommendation(RecommendationContext(
        well_id="WELL-001", risk_type="stuck_pipe", probability=alert.probability,
        severity=alert.severity or "high", depth_m=2920, formation="F3",
        prediction_id="P-001", alert_reason=alert.reason,
        evidence=[EvidenceItem(
            source_id="EV-OFFSET", source_type="historical_event",
            well_id="WELL-002", event_type="stuck_pipe", similarity=0.88,
            depth_m=2950, formation="F3", summary="Historical stuck-pipe event in same formation.",
        )],
    ))
    assert rec.evidence_sufficient
    assert rec.recommendation_id


def test_realtime_ertmac_to_anomaly_to_prediction_callback():
    seen = []

    async def callback(update):
        seen.append(update)
        return {"risk_type": "torque_spike", "probability": 0.91}

    pipeline = RealtimePipeline(
        prediction_callback=callback,
        limits=ParameterLimits(torque=(0, 100), pressure=(0, 1000)),
    )
    update = DrillingParameterUpdate(
        well_id="WELL-001", depth=2920, rop=4, wob=30, rpm=70,
        torque=150, pressure=400, mud_flow=180, mud_weight=11.2,
    )
    event = asyncio.run(pipeline.process(update))
    assert event.event_type == "abnormal_parameter"
    assert "torque" in event.abnormal_fields
    assert len(seen) == 1
