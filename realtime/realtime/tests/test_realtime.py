import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from realtime.adapters import MockERTMACAdapter
from realtime.api import build_router
from realtime.models import DrillingParameterUpdate
from realtime.normalizer import normalize_update
from realtime.pipeline import RealtimePipeline
from realtime.validator import validate_update


def test_normalizer_maps_provider_aliases():
    payload = {
        "depth_m": 2500,
        "rop_m_per_hr": 6,
        "weight_on_bit": 20,
        "rotary_speed": 90,
        "torque": 50,
        "pump_pressure": 300,
        "mud_flow_rate": 180,
        "mud_weight_ppg": 10.5,
    }
    update = normalize_update(payload, well_id="W-001")
    assert update.well_id == "W-001"
    assert update.depth == 2500
    assert update.mud_flow == 180


def test_validator_detects_abnormal_values():
    update = DrillingParameterUpdate(
        well_id="W-001", depth=2500, rop=5, wob=20, rpm=90,
        torque=700, pressure=300, mud_flow=180, mud_weight=10.5,
    )
    issues = validate_update(update)
    assert any(issue.field == "torque" for issue in issues)


@pytest.mark.asyncio
async def test_mock_adapter_generates_canonical_updates():
    adapter = MockERTMACAdapter(interval_seconds=0.001, seed=1)
    stop = asyncio.Event()
    stream = adapter.stream("W-001", stop)
    update = await anext(stream)
    stop.set()
    assert update.well_id == "W-001"
    assert update.depth > 0
    assert update.rop >= 0


@pytest.mark.asyncio
async def test_pipeline_calls_prediction_callback():
    calls = []

    async def callback(update):
        calls.append(update)

    pipeline = RealtimePipeline(prediction_callback=callback)
    update = DrillingParameterUpdate(
        well_id="W-001", depth=2500, rop=5, wob=20, rpm=90,
        torque=50, pressure=300, mud_flow=180, mud_weight=10.5,
    )
    event = await pipeline.process(update)
    assert event.event_type == "parameter_update"
    assert len(calls) == 1


def test_websocket_stream_start_and_stop():
    app = FastAPI()
    app.include_router(build_router(MockERTMACAdapter(interval_seconds=0.001, seed=2)))
    client = TestClient(app)

    with client.websocket_connect("/ws/realtime/W-001") as websocket:
        first = websocket.receive_json()
        assert first["event_type"] == "stream_status"
        websocket.send_json({"action": "ping"})
        messages = [websocket.receive_json() for _ in range(5)]
        assert any(message["event_type"] == "pong" for message in messages)
        websocket.send_json({"action": "stop"})
        for _ in range(10):
            stopped = websocket.receive_json()
            if stopped.get("event_type") == "stream_status" and stopped.get("running") is False:
                break
        else:
            raise AssertionError("stop status was not received")
