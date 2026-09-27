# NWIS eRTMAC Real-Time Integration Layer

Standalone adapter layer for real-time drilling parameters. The current implementation uses a synthetic `MockERTMACAdapter`; a future production eRTMAC adapter can implement the same `ERTMACAdapter` interface without changing validation, normalization, prediction forwarding, or WebSocket consumers.

## Flow

```text
eRTMAC Adapter
      ↓
DrillingParameterUpdate
      ↓
Validation / Normalization
      ↓
RealtimePipeline
      ↓
WebSocket Event Stream
      ↓
PredictionServiceAdapter
```

## Run

```bash
pip install -r requirements.txt
python -m realtime
```

The standalone service runs on `http://localhost:8001`.

WebSocket:

```text
ws://localhost:8001/ws/realtime/WELL-001
```

## WebSocket commands

```json
{"action":"start"}
```

```json
{"action":"stop"}
```

```json
{"action":"ping"}
```

A client can also send a raw provider-style payload for normalization/testing.

## Example event

```json
{
  "event_type": "parameter_update",
  "well_id": "WELL-001",
  "timestamp": "2026-09-28T00:00:00Z",
  "parameters": {
    "well_id": "WELL-001",
    "depth": 2571.2,
    "rop": 6.1,
    "wob": 22.4,
    "rpm": 94.0,
    "torque": 51.7,
    "pressure": 312.5,
    "mud_flow": 184.2,
    "mud_weight": 10.6,
    "source": "mock_ertmac_synthetic"
  },
  "abnormal_fields": [],
  "issues": [],
  "source": "mock_ertmac_synthetic"
}
```

## Integration into existing NWIS backend

Do not copy the implementation into `backend_api`. Instead:

```python
from realtime.api import build_router
from realtime.factory import create_ertmac_adapter

app.include_router(
    build_router(create_ertmac_adapter()),
)
```

If the backend process uses a different Python path, add this module to the deployment package or install it as an internal package.

The requested endpoint will then be:

```text
/ws/realtime/{well_id}
```

The existing NWIS `/api/v1/realtime/ws` endpoint is intentionally not modified by this module.

## Production eRTMAC adapter

Implement:

```python
class OILErtmacAdapter(ERTMACAdapter):
    name = "oil_ertmac"

    async def stream(self, well_id, stop_event):
        # Connect to the officially supplied provider API here.
        # Convert provider messages to DrillingParameterUpdate.
        yield update
```

Then register it in `factory.py`. No downstream WebSocket, validation, normalization, or prediction code needs to change.

## Synthetic data disclaimer

Mock values are synthetic development data. They are not OIL eRTMAC data and must not be used for operational drilling decisions.
