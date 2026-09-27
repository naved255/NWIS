# NWIS Integration Rules

1. Preserve `well_id` and `document_id`; do not create alternate identifiers per module.
2. Pydantic models are the source of truth for Python module boundaries.
3. Backend API responses are versioned under `/api/v1`; `/api` is a compatibility alias.
4. Frontend code must call the backend contract, then map backend data into UI-specific view models.
5. ML inference must use the same feature engineering pipeline used during training.
6. SHAP must explain the exact engineered feature row consumed by the model.
7. RAG evidence must retain source URI/name and page metadata.
8. GeoJSON coordinates are always `[lon, lat]`.
9. Realtime provider adapters must emit `DrillingParameterUpdate`; provider-specific payloads must not leak downstream.
10. Alerts cannot fabricate historical evidence; recommendations must disclose insufficient evidence.
11. Development/mock data must remain explicitly identifiable as synthetic/demo data.
12. Database/PostGIS is the persistence boundary; module logic must not duplicate spatial SQL.
