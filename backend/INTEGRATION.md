# NWIS Backend Integration Guide

## Service ownership

| HTTP group | Backend interface | Intended implementation |
|---|---|---|
| `/wells*` | `WellService` | Existing PostgreSQL/PostGIS repository + future Geo service |
| `/documents`, `/search`, `/rag` | `KnowledgeService` | Document DB + RAG module |
| `/predictions*` | `PredictionService` | Existing `nwis_ml` risk engine + explainability adapter |
| `/alerts` | `AlertService` | Alerting module |
| `/recommendations` | `RecommendationService` | Recommendation module |
| `/realtime` | `RealtimeService` | eRTMAC/realtime module |

## Connecting the existing database

The provided `DatabaseWellService` uses the existing `database.repositories.WellRepository` and `database.models` rather than reproducing PostGIS logic.

From the NWIS repository root, make `database` importable and set:

```env
NWIS_ENABLE_DATABASE=true
NWIS_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/nwis
```

Then install both the backend API requirements and the existing database module requirements.

## Replacing mock services

Implement an interface-compatible adapter and replace its dependency provider in `app/dependencies.py`.

Example:

```python
class RealRAGService(KnowledgeService):
    def __init__(self, rag_service):
        self.rag = rag_service

    def search(self, query, filters, limit):
        # Map RAG service output to app.schemas.SearchResult.
        ...
```

Do not import RAG internals from routers.

## ML integration

The existing risk engine exposes a `RiskPrediction` Pydantic model and `RiskPredictionEngine.predict_risk(...)`. An adapter should:

1. Convert `RiskPredictionRequest.features` into the engine input.
2. Call the existing engine.
3. Convert its output to `RiskPredictionResponse`.
4. Add persistence only if the prediction-storage module owns that responsibility.

The API layer should not train models.

## Frontend

Set:

```env
VITE_NWIS_API_URL=http://localhost:8000/api/v1
```

Use `/api/v1` for all new React calls. The unversioned `/api` alias is retained for migration compatibility.
