# API Compatibility Report

## Canonical API
Backend exposes `/api/v1` and retains `/api` as a compatibility alias.

## Frontend live adapter
All live API calls now use the canonical backend contract:
- wells
- nearby wells
- monitoring
- trend
- events
- predictions
- alerts
- knowledge search

UI-specific naming differences such as `well_id` -> `id` and `risk_type` -> `riskType` are handled only in the frontend adapter.

## Realtime
The backend's existing `/api/v1/realtime/ws` remains a stable mock/development WebSocket. The dedicated realtime module exposes the richer well-scoped stream under `/ws/realtime/{well_id}` and its REST lifecycle endpoints. A future production integration should mount the realtime module router into the main API rather than maintain two independent realtime implementations.

## RAG
RAG uses its own `RetrievalResponse` / `EvidenceItem` contract. Backend `SearchResult` is an API presentation model, so an adapter is required; the current backend still uses `MockKnowledgeService` by default.

## ML / SHAP
ML `RiskPrediction` and backend `RiskPredictionResponse` are intentionally different layers. The backend response includes API identifiers and timestamps; the ML engine owns probability/severity/model-version fields. SHAP consumes the engineered model input, not raw pre-engineering data.

## Geo
Geo module produces map-ready GeoJSON and backend has its own nearby-well API response. The frontend consumes backend nearby-well responses; GeoJSON is available for direct map integrations.
