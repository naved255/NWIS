# NWIS Data Ingestion Layer

Independent ingestion layer for the AI-Powered Nearby Wells Intelligence System (SIH 26121).

## Scope

This module ingests CSV/JSON files and provides adapters for HTTP APIs, databases, and PDFs. It normalizes field names, converts common missing-value markers to `None`, validates records with Pydantic, attaches source metadata, detects duplicate records using deterministic content fingerprints, and returns standardized NWIS entities.

PDF extraction deliberately stops at the adapter boundary. OCR/NLP/document understanding should be implemented by the document-processing/RAG modules.

## Quick test

From this directory:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Expected: all tests pass.

## Minimal usage

```python
from ingestion import IngestionEngine, CSVDataSource

engine = IngestionEngine()
result = engine.ingest(CSVDataSource("samples/wells.csv"), "well")

print(result.accepted_count)
print(result.duplicate_count)
print(result.error_count)
for well in result.accepted:
    print(well.model_dump(mode="json"))
```

## Supported entity types

- `well` -> `Well`
- `drilling_parameter` -> `DrillingParameter`
- `drilling_event` -> `DrillingEvent`
- `trajectory_point` -> `TrajectoryPoint`
- `document_metadata` -> `DocumentMetadata`

## Integration boundary

Other modules should depend on `ingestion.IngestionEngine` and the Pydantic entities, not on CSV/JSON implementation details. A future application service can persist `result.accepted` to PostgreSQL/PostGIS, publish events, or pass records to ML/RAG services.

For a SQLAlchemy application, wrap a query in a callable and provide it to `DatabaseDataSource`. This keeps the ingestion package independent from a particular database driver.

## Source metadata

Every entity includes `source_metadata` with `source_type`, `source_name`, `source_uri`, optional `source_record_id`, ingestion timestamp, and schema version.
