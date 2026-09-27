# NWIS Persistent Storage Layer

Isolated database/storage module for the AI-Powered Nearby Wells Intelligence System (NWIS).

## Scope

- PostgreSQL + PostGIS persistence using SQLAlchemy 2.x.
- Pydantic v2 request/response schemas.
- Qdrant adapter for document/chunk embeddings and metadata.
- Object-storage abstraction with a local filesystem implementation and S3-compatible implementation.
- Alembic migration setup.
- Sample seed data (synthetic and explicitly marked as such).
- Repository functions for well, spatial, event, drilling-parameter, formation and similar-well metadata retrieval.

This module deliberately does **not** implement RAG, ML prediction, alert decision logic, or frontend functionality.

## Layout

```text
database/
  config.py
  db.py
  models/
  schemas/
  repositories/
  qdrant/
  storage/
  alembic/
    env.py
    script.py.mako
    versions/0001_initial_schema.py
  scripts/seed.py
  tests/
requirements.txt
.env.example
Dockerfile.postgis
docker-compose.yml
```

## Quick start

```bash
cp .env.example .env
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
alembic -c database/alembic.ini upgrade head
python -m database.scripts.seed
```

PostGIS can be started with:

```bash
docker compose up -d postgres qdrant
```

Then run migrations and seed.

## Integration

Copy the `database/` package into the NWIS repository root. Other modules should import only the public repository/schema/storage interfaces rather than depending on ORM internals.

Example:

```python
from database.repositories.wells import WellRepository

repo = WellRepository(session)
well = repo.get_well("WELL-DEMO-001")
nearby = repo.get_nearby_wells("WELL-DEMO-001", radius_km=10)
```

For Qdrant:

```python
from database.qdrant.client import QdrantVectorStore

store = QdrantVectorStore.from_settings()
store.upsert_chunks([...])
```
