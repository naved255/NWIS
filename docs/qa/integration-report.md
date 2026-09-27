# NWIS Integration Report

## Scope
Reviewed: `docs/`, `contracts/`, `backend/`, `frontend/`, `ml/`, `rag/`, `ingestion/`, `geo/`, `realtime/`, `document_intelligence/`, `nwis_nlp_extraction/`, `explainability_decision_support/`, `database/`, and `tests/`.

## Findings fixed

### 1. SHAP / ML Pipeline incompatibility — fixed
The ML engine persists a sklearn `Pipeline` containing preprocessing + LightGBM. The SHAP module attempted `TreeExplainer(pipeline)` and failed. The explainability service now unwraps the pipeline, transforms the exact input row with its fitted preprocessor, and explains the underlying tree model.

### 2. Geo test package-name mismatch — fixed
Tests imported `geo_spatial.*`, while the repository package is `geo.*`.

### 3. Document Intelligence test package-name mismatch — fixed
Tests imported `ingestion.document_intelligence.*`, while the delivered module is top-level `document_intelligence`.

### 4. Backend/frontend API mismatch — fixed
The frontend live adapter referenced `/overview`, `/risks`, `/compare`, and other non-contract endpoints. It now targets `/api/v1` canonical endpoints and maps API responses into the UI view model. Backend monitoring/trend endpoints were added to expose the existing drilling-parameter boundary.

### 5. Root contracts were empty — fixed
The six JSON contracts were generated from the active Pydantic models and the root Markdown contract documents were populated.

## Verified compatibility

- Pydantic validation: pass.
- Backend OpenAPI route presence: pass.
- GeoJSON Point/FeatureCollection shape: pass.
- RAG evidence retrieval with an adapter-compatible fake store: pass.
- LightGBM training/inference: pass.
- SHAP explanation on the persisted pipeline: pass.
- Alert rule evaluation with historical evidence: pass.
- Evidence-backed recommendation generation: pass.
- eRTMAC normalization/anomaly callback: pass.
- End-to-end historical pipeline test: pass.
- Explicit ingestion-to-database field mapping test: pass.

## Remaining infrastructure dependencies

Production deployment still requires:
- PostgreSQL + PostGIS
- Qdrant and its configured embeddings
- a real approved OCR engine/model if scanned documents are used
- production eRTMAC adapter/credentials/network access
- the frontend Node dependency installation/build
- production ML artifacts/model versions

These are deployment prerequisites, not silent fallbacks.
