
from fastapi.testclient import TestClient

from app.main import app


def test_backend_contract_endpoints_and_frontend_paths():
    client = TestClient(app)
    assert client.get("/api/v1/health").status_code == 200
    openapi = client.get("/openapi.json").json()["paths"]

    required = {
        ("GET", "/api/v1/wells"),
        ("GET", "/api/v1/wells/{well_id}"),
        ("GET", "/api/v1/wells/{well_id}/monitoring"),
        ("GET", "/api/v1/wells/{well_id}/trend"),
        ("GET", "/api/v1/wells/{well_id}/events"),
        ("GET", "/api/v1/wells/nearby"),
        ("GET", "/api/v1/predictions"),
        ("POST", "/api/v1/predictions/risk"),
        ("GET", "/api/v1/alerts"),
        ("GET", "/api/v1/recommendations"),
        ("POST", "/api/v1/search"),
        ("POST", "/api/v1/rag"),
        ("GET", "/api/v1/realtime/status"),
    }
    for method, path in required:
        assert path in openapi, path
        assert method.lower() in openapi[path], (method, path)


def test_frontend_real_api_uses_existing_backend_contract():
    source = open("frontend/src/api/index.js", encoding="utf-8").read()
    expected_fragments = [
        "apiClient.get('/wells')",
        "apiClient.get('/predictions'",
        "apiClient.get('/alerts'",
        "apiClient.post('/search'",
        "apiClient.get(`/wells/${id}/monitoring`)",
        "apiClient.get(`/wells/${id}/trend`)",
    ]
    for fragment in expected_fragments:
        assert fragment in source
    assert "/overview" not in source
    assert "/risks" not in source


def test_ingestion_database_field_mapping_is_explicit():
    from datetime import datetime, timezone
    from ingestion.models.entities import SourceMetadata, Well, DrillingParameter, DrillingEvent
    from backend.app.services.ingestion_mapping import (
        well_to_db_values, drilling_parameter_to_db_values, drilling_event_to_db_values,
    )
    source = SourceMetadata(source_type="sample", source_name="qa")
    w = Well(well_id="W1", block="B1", total_depth=3000, source_metadata=source)
    p = DrillingParameter(well_id="W1", observed_at=datetime.now(timezone.utc), mud_flow_rate=1800, standpipe_pressure=12000, source_metadata=source)
    e = DrillingEvent(well_id="W1", event_type="MUD_LOSS", duration_minutes=30, source_metadata=source)
    assert well_to_db_values(w)["block_name"] == "B1"
    assert well_to_db_values(w)["total_depth_m"] == 3000
    assert drilling_parameter_to_db_values(p)["flow_rate_lpm"] == 1800
    assert drilling_parameter_to_db_values(p)["standpipe_pressure_kpa"] == 12000
    assert drilling_event_to_db_values(e)["duration_min"] == 30
