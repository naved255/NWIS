"""Insert synthetic NWIS seed records for development/testing only."""
from datetime import datetime, timezone
from decimal import Decimal
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from database.db import SessionLocal
from database.models import Well, WellTrajectory, Formation, GeologicalInformation, DrillingEvent, DrillingParameter, Document, DocumentChunk, ModelVersion, Prediction, Alert, Recommendation, User


SAMPLE_NOTE = "SYNTHETIC SAMPLE DATA - NOT REAL OIL INDIA LIMITED DATA"


def seed() -> None:
    with SessionLocal() as session:
        if session.scalar(select(Well).where(Well.well_id == "NWIS-DEMO-001")):
            print("Seed data already present")
            return
        now = datetime.now(timezone.utc)
        wells = [
            Well(well_id="NWIS-DEMO-001", well_name="Demo Well Alpha", field_name="Demo Field", operator="SAMPLE", status="COMPLETED", latitude=Decimal("27.500000"), longitude=Decimal("95.200000"), total_depth_m=Decimal("3200"), surface_location=WKTElement("POINT(95.2 27.5)", srid=4326), metadata_json={"source": "synthetic", "note": SAMPLE_NOTE}),
            Well(well_id="NWIS-DEMO-002", well_name="Demo Well Beta", field_name="Demo Field", operator="SAMPLE", status="COMPLETED", latitude=Decimal("27.530000"), longitude=Decimal("95.220000"), total_depth_m=Decimal("3050"), surface_location=WKTElement("POINT(95.22 27.53)", srid=4326), metadata_json={"source": "synthetic", "note": SAMPLE_NOTE}),
            Well(well_id="NWIS-DEMO-003", well_name="Demo Well Gamma", field_name="Adjacent Field", operator="SAMPLE", status="DRILLED", latitude=Decimal("27.650000"), longitude=Decimal("95.350000"), total_depth_m=Decimal("3500"), surface_location=WKTElement("POINT(95.35 27.65)", srid=4326), metadata_json={"source": "synthetic", "note": SAMPLE_NOTE}),
        ]
        session.add_all(wells)
        session.flush()
        for well in wells:
            session.add_all([
                Formation(well_id=well.id, formation_name="Demo Sandstone", top_depth_m=Decimal("1800"), base_depth_m=Decimal("2300"), lithology="sandstone", age="Demo", stratigraphic_group="Demo Group", properties={"source": "synthetic"}),
                GeologicalInformation(well_id=well.id, depth_from_m=Decimal("1800"), depth_to_m=Decimal("2300"), lithology="sandstone", porosity_pct=Decimal("18.2"), permeability_md=Decimal("42"), pressure_kpa=Decimal("22000"), temperature_c=Decimal("82"), properties={"source": "synthetic"}),
                DrillingEvent(well_id=well.id, event_type="FORMATION_ENTRY", event_time=now, depth_m=Decimal("1800"), severity="INFO", description="Synthetic formation-entry event", metadata_json={"source": "synthetic"}),
                DrillingParameter(well_id=well.id, recorded_at=now, measured_depth_m=Decimal("1800"), weight_on_bit_kn=Decimal("90"), rotary_rpm=Decimal("120"), torque_kn_m=Decimal("8"), rate_of_penetration_m_hr=Decimal("18"), standpipe_pressure_kpa=Decimal("12000"), flow_rate_lpm=Decimal("1800"), mud_weight_kg_m3=Decimal("1180"), mud_viscosity_cp=Decimal("32"), metadata_json={"source": "synthetic"}),
                WellTrajectory(well_id=well.id, measured_depth_m=Decimal("0"), tvd_m=Decimal("0"), sequence_no=0, point=WKTElement(f"POINT Z({well.longitude} {well.latitude} 0)", srid=4326), metadata_json={"source": "synthetic"}),
                WellTrajectory(well_id=well.id, measured_depth_m=Decimal("1500"), tvd_m=Decimal("1490"), inclination_deg=Decimal("2.5"), azimuth_deg=Decimal("90"), sequence_no=1, point=WKTElement(f"POINT Z({well.longitude} {well.latitude} 1500)", srid=4326), metadata_json={"source": "synthetic"}),
            ])
        doc = Document(document_id="DOC-DEMO-001", well_id=wells[0].id, document_type="WCR", title="Synthetic Well Completion Report", storage_key="demo/NWIS-DEMO-001/wcr-demo.pdf", mime_type="application/pdf", page_count=1, metadata_json={"source": "synthetic", "note": SAMPLE_NOTE})
        session.add(doc)
        session.flush()
        session.add(DocumentChunk(document_id=doc.id, chunk_index=0, text="Synthetic document chunk for development only.", page_number=1, formation="Demo Sandstone", depth_from_m=Decimal("1800"), depth_to_m=Decimal("1850"), event_type="FORMATION_ENTRY", qdrant_point_id="demo-point-001", metadata_json={"source": "synthetic"}))
        model_version = ModelVersion(model_name="demo-risk-model", version="0.1.0", artifact_uri="local://synthetic/demo", metrics={"note": SAMPLE_NOTE}, feature_schema={"type": "demo"}, is_active=False, metadata_json={"source": "synthetic"})
        session.add(model_version)
        session.flush()
        prediction = Prediction(well_id=wells[0].id, model_version_id=model_version.id, prediction_type="DEMO_RISK", predicted_value=Decimal("0.25"), risk_score=Decimal("0.250000"), severity="LOW", predicted_at=now, explanation={"note": SAMPLE_NOTE}, input_snapshot={"synthetic": True})
        session.add(prediction)
        session.flush()
        session.add(Alert(well_id=wells[0].id, prediction_id=prediction.id, alert_type="DEMO_ALERT", severity="LOW", status="OPEN", message="Synthetic development alert", triggered_at=now, metadata_json={"source": "synthetic"}))
        session.add(Recommendation(well_id=wells[0].id, prediction_id=prediction.id, recommendation_type="DEMO", priority="LOW", title="Synthetic recommendation", description="Synthetic development recommendation only.", rationale=SAMPLE_NOTE, status="NEW", metadata_json={"source": "synthetic"}))
        session.add(User(username="demo_engineer", email="demo.engineer@example.invalid", role="ENGINEER", is_active=True, metadata_json={"source": "synthetic", "note": SAMPLE_NOTE}))
        session.commit()
        print("Inserted synthetic NWIS seed data")


if __name__ == "__main__":
    seed()
