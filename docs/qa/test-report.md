# NWIS Test Report

## Repository integration suite

Command:

```bash
PYTHONPATH=. PYTHONPATH=... python -m pytest -q
```

Result: **3 passed**.

Coverage:
1. Historical document -> OCR -> NLP -> canonical DB entities -> vector/RAG -> geo/GeoJSON -> LightGBM prediction -> SHAP -> alert -> recommendation.
2. eRTMAC-style realtime payload -> validation/anomaly detection -> prediction callback.

## Existing module suites

- Backend: **PASS**
- ML: **4 passed**
- Ingestion: **PASS**
- Realtime: **PASS**
- NLP extraction: **6 passed**
- Explainability/decision support: **6 passed**
- Geo: **PASS after correcting stale imports**
- Document Intelligence: **PASS after correcting stale imports**.

## Warnings

The integration ML test emits sklearn feature-name warnings from the existing prediction path. The prediction remains successful; this should be cleaned up in a future ML-specific refinement by consistently passing DataFrames through inference.

The execution environment also emits an unrelated artifact-tool spreadsheet warmup traceback during Python startup; it did not cause any NWIS test failure.

## Frontend

`npm install` could not complete within the available execution window, so the React/Vite test/build was not claimed as executed. Static frontend/backend contract checks and explicit ingestion→database field mapping checks were added and passed as part of the repository integration suite.
