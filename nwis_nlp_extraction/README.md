# NWIS NLP Information Extraction Module

Standalone NLP module for the **AI-Powered Nearby Wells Intelligence System (NWIS)**.
It converts text/pages produced by the document-processing module into structured drilling knowledge.

## Scope

This module extracts:

- well names/IDs
- formation observations
- depths
- drilling parameters
- mud losses
- kicks
- stuck pipe
- fishing events
- NPT
- cementing problems
- casing events/information
- mud-program observations
- pressure observations
- mitigation actions
- operational recommendations
- lessons learned
- dates
- equipment
- severity

It does **not** implement RAG, vector storage, risk prediction, or an external LLM dependency.

## Architecture

```text
Document Processor
      |
      | DocumentInput JSON/Pydantic
      v
+-----------------------------+
| DrillingNLPExtractor        |
|                             |
|  +-----------------------+  |
|  | RuleBasedExtractor    |  |  <-- always enabled
|  +-----------------------+  |
|             |               |
|      +------+-------+       |
|      |              |       |
|   spaCy NER   Transformer NER   <-- optional adapters
|      |              |       |
+------+--------------+-------+
       |
       v
ExtractionResult
  |-- ExtractedEntity[]
  |-- DrillingEvent[]
  |-- FormationObservation[]
  |-- MitigationAction[]
  `-- LessonLearned[]
```

Every object carries `Provenance` containing `document_id`, `page_number`, `text_span`, and `source_text`.

## Folder structure

```text
nwis_nlp_extraction/
├── nlp_extraction/
│   ├── __init__.py
│   ├── api.py
│   ├── pipeline.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── extractors/
│       ├── __init__.py
│       ├── rule_based.py
│       ├── spacy_ner.py
│       └── transformer_ner.py
├── tests/
│   └── test_pipeline.py
├── requirements.txt
├── requirements-optional.txt
├── pyproject.toml
└── README.md
```

## Input contract

The document-processing module sends:

```json
{
  "document_id": "WCR-0001",
  "pages": [
    {
      "page_number": 12,
      "text": "At 2840 m severe mud loss occurred while drilling through the Barail Formation."
    }
  ],
  "metadata": {}
}
```

The design deliberately accepts **page-level text** so provenance can point back to the original document page.

## Python interface

```python
from nlp_extraction import DrillingNLPExtractor
from nlp_extraction.models import DocumentInput, DocumentPage

extractor = DrillingNLPExtractor()
result = extractor.extract(
    DocumentInput(
        document_id="WCR-0001",
        pages=[DocumentPage(page_number=12, text="At 2840 m severe mud loss occurred.")],
    )
)
```

## Example output

For:

```text
At 2840 m severe mud loss occurred while drilling through the Barail Formation.
```

The event is approximately:

```json
{
  "event_type": "MUD_LOSS",
  "depth_m": 2840,
  "severity": "HIGH",
  "provenance": {
    "document_id": "WCR-0001",
    "page_number": 12,
    "text_span": [0, 76],
    "source_text": "At 2840 m severe mud loss occurred while drilling through the Barail Formation."
  }
}
```

## Contextual extraction rule

The module does not convert every keyword occurrence into an event. Ambiguous terms such as `fishing`, `NPT`, `casing`, and pressure observations require incident/operation context. For example:

```text
Fishing tools were available in the warehouse.
```

is **not** emitted as a FISHING event.

But:

```text
Fishing operation was initiated after the BHA was left in hole.
```

is emitted as a FISHING event.

## Optional spaCy / Transformer NER

The core rules run without model downloads. To add spaCy:

```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
python -m spacy download en_core_web_sm
```

Set:

```text
NWIS_SPACY_MODEL=en_core_web_sm
```

For a Hugging Face token-classification model:

```text
NWIS_TRANSFORMER_NER_MODEL=<your-approved-model-name>
```

Only use an approved/local model suitable for the project's data and deployment environment. The module does not assume a particular drilling-specific model exists.

## FastAPI interface

Start:

```bash
uvicorn nlp_extraction.api:app --host 0.0.0.0 --port 8001
```

Endpoints:

- `GET /health`
- `POST /v1/nlp/extract`

The API uses the same `DocumentInput` and `ExtractionResult` contracts as the Python interface.

## Installation

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Run tests:

```bash
pytest -q
```

## Integration with NWIS

1. Copy the `nlp_extraction/` package into the backend/NLP service location selected by the main architecture.
2. Keep the document processor responsible for PDF/OCR/table extraction.
3. Convert its output to `DocumentInput`.
4. Call `DrillingNLPExtractor.extract()` or `POST /v1/nlp/extract`.
5. Persist `ExtractionResult` using the database team's schemas. Do not make this module directly depend on SQLAlchemy/PostGIS.
6. Pass `DrillingEvent`, `FormationObservation`, and other standardized objects to downstream ML/RAG/backend services through the shared contracts.
7. Preserve `provenance` when transforming the objects so downstream systems can cite the source document/page/text.

### Stable integration boundary

```text
Document Processing -> DocumentInput -> NLP Extraction -> ExtractionResult
```

No database connection is required by this module. This keeps it independently testable and prevents coupling to an unfinished storage implementation.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `NWIS_SPACY_MODEL` | No | spaCy model name/path |
| `NWIS_TRANSFORMER_NER_MODEL` | No | Hugging Face/local token classification model |

No secrets are required.

## Tests

The test suite covers:

- contextual mud-loss extraction
- depth and severity extraction
- kick/cementing event extraction
- provenance preservation
- well and drilling parameter extraction
- equipment extraction
- mitigation/recommendation extraction
- lesson extraction
- prevention of false event extraction for bare mentions

## Known limitations

- Regex/rule coverage should be expanded as real, approved drilling-document examples become available.
- Severity is lexical; it is not a statistical risk score.
- Formation names can be ambiguous in free text and should be validated against the geological master data when that module is integrated.
- spaCy's generic English model is not drilling-specific.
- Transformer NER is an optional enrichment layer and requires an approved compatible model.
- Table extraction remains the responsibility of the document-processing module.
- Cross-document entity resolution is intentionally outside this module.
- No LLM or external API is required.
