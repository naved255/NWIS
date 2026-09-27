# NWIS Data Contract

## Canonical identifiers
- `well_id` is the stable external well identifier across ingestion, NLP, RAG, geo, ML, realtime, backend and frontend.
- `document_id` identifies a source document and must remain stable through OCR/NLP/RAG.
- `prediction_id`, `alert_id`, and `recommendation_id` link decision-support records.

## Pipeline boundary contracts

| Boundary | Canonical payload | Required traceability |
|---|---|---|
| Document/OCR -> NLP | `DocumentInput` / pages | `document_id`, `page_number`, source text |
| NLP -> persistence | `ExtractionResult`, canonical ingestion entities | well/event IDs + provenance |
| NLP -> RAG | `ChunkRecord` | source URI/name, page, well, event, formation/depth metadata |
| Geo -> API/frontend | `NearbyWellsResponse` / GeoJSON FeatureCollection | `well_id`, coordinates, distance |
| ML -> decision support | `RiskPrediction` | risk type, probability, severity, confidence, model version |
| ML -> SHAP | exact engineered model feature dictionary | same feature names/order/values as inference |
| Alert -> recommendation | `AlertContext` / `EvidenceItem` | prediction/risk/well + evidence |
| Realtime -> ML | `DrillingParameterUpdate` | well, timestamp, sequence, source |

## Database mapping notes

The ingestion models intentionally use domain-neutral names while PostgreSQL models use storage-specific names. The adapter must map:
- `block` -> `block_name`
- `total_depth` -> `total_depth_m`
- `observed_at` -> `recorded_at`
- `mud_flow_rate` -> `flow_rate_lpm`
- `standpipe_pressure` -> `standpipe_pressure_kpa`
- `duration_minutes` -> `duration_min`

No module should silently rename fields at a public API boundary.

## GeoJSON

All map payloads use RFC 7946-style:
- `FeatureCollection`
- `Point` coordinates as `[longitude, latitude]`
- trajectory coordinates as `[longitude, latitude]`

## Realtime

Realtime timestamps are normalized to UTC. Development parameter limits are not production/OIL operating limits.
