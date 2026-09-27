from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] in {"ok", "degraded"}


def test_list_wells():
    response = client.get("/api/v1/wells?limit=10")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body and "pagination" in body
    assert body["items"][0]["well_id"] == "WELL-001"


def test_nearby_wells_route_precedes_well_id_route():
    response = client.get("/api/v1/wells/nearby?well_id=WELL-001&radius_km=10")
    assert response.status_code == 200
    assert response.json()["source_well_id"] == "WELL-001"


def test_risk_prediction():
    response = client.post("/api/v1/predictions/risk", json={"well_id": "WELL-001", "risk_type": "stuck_pipe", "features": {"depth": 2800, "torque": 80}})
    assert response.status_code == 200
    body = response.json()
    assert body["risk_type"] == "stuck_pipe"
    assert 0 <= body["probability"] <= 1


def test_validation_error():
    response = client.get("/api/v1/wells/nearby?well_id=WELL-001&radius_km=-1")
    assert response.status_code == 422


def test_docs():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/v1/wells" in response.json()["paths"]
