# NWIS Backend API

Standalone FastAPI API gateway for the AI-Powered Nearby Wells Intelligence System (NWIS).

## Design

This module is an orchestration/API layer. It does not implement spatial calculations, RAG retrieval, ML training, OCR, realtime ingestion, alert generation, or recommendation logic. Those responsibilities are represented by service interfaces under `app/services/interfaces.py`.

The package starts in **mock mode** so it can be integrated and tested before all NWIS modules are connected. Replace each mock adapter with the corresponding module service without changing the HTTP routers or Pydantic contracts.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Docs: `http://localhost:8000/docs`
OpenAPI: `http://localhost:8000/openapi.json`

Canonical API prefix: `/api/v1`
Compatibility prefix: `/api`

## Database mode

Set `NWIS_ENABLE_DATABASE=true` and `NWIS_DATABASE_URL=...`. The database adapter expects the existing NWIS `database` package to be importable from `PYTHONPATH`.

## Integration strategy

1. Keep routers unchanged.
2. Implement the relevant interface in `app/services/adapters/` or another integration package.
3. Change the dependency provider in `app/dependencies.py` to return the real service.
4. Do not import unfinished module internals into routers.
5. Preserve response models so React clients have a stable contract.
