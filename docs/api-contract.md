# NWIS Backend API Contract

## Base URL

Canonical versioned API:

`/api/v1`

A compatibility alias is also exposed at `/api`. New frontend code should use `/api/v1`.

Swagger UI: `/docs`
ReDoc: `/redoc`
OpenAPI JSON: `/openapi.json`

## Common conventions

- JSON request/response bodies use `application/json`.
- Pagination uses `limit` and `offset` query parameters.
- Pagination responses contain `{items, pagination}`.
- Validation errors are standard FastAPI `422` responses.
- Domain not-found errors are `404` with `{error: {code, message}}`.
- Unexpected errors are `500` without exposing internal exception details.

## 1. Wells

### `GET /api/v1/wells`

Query:

```text
limit=20&offset=0
```

Response:

```json
{
  "items": [
    {
      "id": "w-001",
      "well_id": "WELL-001",
      "well_name": "Sample Well A",
      "field_name": "DEMO-FIELD",
      "block_name": "BLOCK-A",
      "operator": "SAMPLE",
      "status": "DRILLING",
      "latitude": "28.6139",
      "longitude": "77.2090",
      "total_depth_m": "3200",
      "metadata": {"sample": true}
    }
  ],
  "pagination": {"limit": 20, "offset": 0, "total": 1}
}
```

### `GET /api/v1/wells/{well_id}`

Returns one `WellResponse`.

### `GET /api/v1/wells/nearby`

Query:

```text
well_id=WELL-001&radius_km=25&limit=20&offset=0
```

Response contains `source_well_id`, `radius_km`, nearby wells, distance, formation matches, and event types.

### `GET /api/v1/wells/{well_id}/events`

Optional `event_type`, `limit`, and `offset`.

### `GET /api/v1/wells/{well_id}/trajectory`

Returns ordered trajectory points.

## 2. Documents and knowledge

### `GET /api/v1/documents`

Optional `well_id`, `document_type`, `limit`, `offset`.

### `POST /api/v1/search`

Request:

```json
{
  "query": "mud loss around 2800 m",
  "well_id": "WELL-001",
  "document_type": "DDR",
  "event_type": "mud_loss",
  "formation": "F1",
  "limit": 10
}
```

Response:

```json
{
  "query": "mud loss around 2800 m",
  "items": [
    {
      "result_id": "chunk-001",
      "score": 0.91,
      "title": "Sample drilling report",
      "text": "...",
      "source_uri": "mock://DOC-001",
      "document_id": "DOC-001",
      "well_id": "WELL-001",
      "page": 1,
      "metadata": {}
    }
  ]
}
```

### `POST /api/v1/rag`

Request:

```json
{
  "query": "What happened in nearby wells around 2800-3000 m?",
  "well_id": "WELL-001",
  "include_sources": true,
  "limit": 5
}
```

Response:

```json
{
  "question": "What happened in nearby wells around 2800-3000 m?",
  "answer": "...",
  "sources": []
}
```

## 3. Predictions

### `GET /api/v1/predictions`

Optional `well_id`, `risk_type`, `limit`, `offset`.

### `POST /api/v1/predictions/risk`

Request:

```json
{
  "well_id": "WELL-001",
  "risk_type": "stuck_pipe",
  "features": {
    "depth": 2940,
    "rop": 5,
    "wob": 25,
    "rpm": 90,
    "torque": 78,
    "pressure": 350,
    "mud_flow": 200,
    "mud_weight": 10.5
  }
}
```

Response:

```json
{
  "prediction_id": "uuid",
  "well_id": "WELL-001",
  "risk_type": "stuck_pipe",
  "probability": 0.73,
  "severity": "high",
  "confidence": 0.82,
  "model_version": "1.0.0",
  "explanation": {},
  "predicted_at": "2026-09-27T18:30:00Z"
}
```

The backend only transports the ML service result. SHAP/explainability remains owned by the ML/explainability module.

## 4. Alerts

### `GET /api/v1/alerts`

Optional `well_id`, `status`, `limit`, `offset`.

Response item:

```json
{
  "id": "alert-001",
  "well_id": "WELL-001",
  "prediction_id": "prediction-id",
  "alert_type": "stuck_pipe",
  "severity": "high",
  "status": "OPEN",
  "message": "Potential stuck pipe risk detected.",
  "triggered_at": "2026-09-27T18:30:00Z",
  "metadata": {}
}
```

## 5. Recommendations

### `GET /api/v1/recommendations`

Optional `well_id`, `status`, `limit`, `offset`.

## 6. Realtime

### `GET /api/v1/realtime/status`

Returns realtime adapter state.

### `WS /api/v1/realtime/ws`

WebSocket endpoint for future eRTMAC event streaming. The current mock adapter sends one status message and closes the connection.

## 7. Health

### `GET /api/v1/health`

Response:

```json
{
  "status": "ok",
  "service": "NWIS Backend API",
  "version": "v1",
  "dependencies": {
    "api": "ok",
    "database": "mock",
    "knowledge": "mock",
    "ml": "mock",
    "realtime": "mock"
  }
}
```

## React integration example

```js
const API_BASE = import.meta.env.VITE_NWIS_API_URL || 'http://localhost:8000/api/v1';

const response = await fetch(`${API_BASE}/wells/WELL-001`);
const well = await response.json();

const predictionResponse = await fetch(`${API_BASE}/predictions/risk`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    well_id: 'WELL-001',
    features: {depth: 2800, torque: 80}
  })
});
const prediction = await predictionResponse.json();
```

## Frontend compatibility additions

The frontend live adapter now uses only the canonical `/api/v1` API:
- `GET /wells`
- `GET /wells/{well_id}`
- `GET /wells/{well_id}/monitoring`
- `GET /wells/{well_id}/trend`
- `GET /wells/{well_id}/events`
- `GET /wells/nearby`
- `GET /predictions`
- `GET /alerts`
- `POST /search`

The previous frontend-only `/overview`, `/risks`, `/compare`, and `/trend` assumptions were removed from the live adapter. UI-specific transformations are kept in `frontend/src/api/index.js`.
