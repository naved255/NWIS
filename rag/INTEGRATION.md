# NWIS RAG Integration Guide

## 1. Add the module to PYTHONPATH

From the NWIS repository root:

```bash
pip install -r rag/requirements.txt
```

For editable package installation:

```bash
pip install -e rag
```

## 2. Start Qdrant

Use an existing NWIS Qdrant deployment or run one locally:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Set `QDRANT_URL` if it is not local.

## 3. Index output from document/NLP processing

The document pipeline should convert its output into `ChunkRecord` and call:

```python
from nwis_rag.indexer import index_chunks
index_chunks(records, rag.store)
```

The RAG module does not read raw PDFs. That separation keeps OCR/document processing independently replaceable.

## 4. Backend integration

A FastAPI route can instantiate one `RAGService` at application startup and call:

```python
rag.retrieve_similar_documents(query, filters=filters)
rag.retrieve_similar_events(query, event_type=event_type, filters=filters)
rag.retrieve_offset_well_knowledge(query, location=location, target_well_id=target_well_id)
rag.answer_question(question, filters=filters)
```

Recommended HTTP response serialization is directly from the Pydantic models.

## 5. Offset wells

The `geo` module should first determine nearby/offset wells. It can then pass a normalized `location` and/or a set of well IDs to a future adapter. This RAG module intentionally does not duplicate spatial calculations.

## 6. Source guarantees

Every `EvidenceItem` contains:

- `evidence_id`
- `source_uri`
- `source_name`
- optional `page`
- metadata

`AnswerResponse.source` is generated from those retrieved objects, not from free-form LLM output.

## 7. LLM integration

The RAG module has no provider-specific LLM dependency. This avoids coupling NWIS to a particular vendor. Inject a callable into `EvidenceAnswerer` that accepts the generated evidence-only prompt and returns text.

If the LLM output omits sources, the service still returns the actual retrieved source list.
