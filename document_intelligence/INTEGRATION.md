# NWIS Document Intelligence — Integration Package

## 1. Architecture

```text
PDF / Image
    |
    v
File validation
    |
    +--> PDF native text extraction (PyMuPDF)
    |          |
    |          +--> selectable text? --> yes --> cleaning
    |          |
    |          +--> no --> render page --> OCR adapter --> cleaning
    |
    +--> image --> OCR adapter --> cleaning
    |
    v
Page segmentation
    |
    +--> table extraction (PyMuPDF, optional pdfplumber fallback)
    |
    v
Deterministic metadata extraction
    |
    v
StructuredDocument (Pydantic / JSON)
    |
    +--> NLP module
    +--> RAG ingestion module
```

This module does not implement embeddings, semantic RAG, similarity search, risk prediction, SHAP, alerts, or dashboard functionality.

## 2. Folder/file structure

```text
ingestion/document_intelligence/
├── __init__.py
├── config.py
├── factory.py
├── integration_example.py
├── metadata.py
├── models.py
├── pipeline.py
├── segmentation.py
├── validators.py
├── requirements.txt
├── .env.example
├── README.md
├── MODULE_CONTRACT.md
├── INTEGRATION.md
├── ocr/
│   ├── __init__.py
│   ├── base.py
│   ├── tesseract_adapter.py
│   └── paddle_adapter.py
├── tables/
│   ├── __init__.py
│   └── extractor.py
└── tests/
    ├── conftest.py
    ├── test_models.py
    ├── test_pipeline.py
    └── sample_documents/sample_ddr.pdf
```

## 3. Complete implementation

All source code is included in this package. The public entry point is:

```python
from ingestion.document_intelligence import DocumentIntelligencePipeline
```

For environment-driven construction:

```python
from ingestion.document_intelligence.factory import create_pipeline
pipeline = create_pipeline()
```

## 4. API/interface definitions

### `DocumentIntelligencePipeline.process`

```text
process(path, document_id=None, document_type=None) -> StructuredDocument
```

Inputs:
- `path`: PDF or supported image path.
- `document_id`: optional stable upstream identifier. If absent, a SHA-256 content-derived ID is generated.
- `document_type`: optional explicit type such as `DDR` or `WCR`.

### OCR interface

```text
OCRAdapter.extract_text(image: PIL.Image) -> str
```

Any future OCR provider can implement this interface without changing the pipeline.

## 5. Data models

`models.py` defines:
- `Provenance`
- `Page`
- `Section`
- `TableCell`
- `ExtractedTable`
- `DocumentMetadata`
- `StructuredDocument`

All page/section/table records preserve the required provenance fields.

## 6. Installation

```bash
pip install -r ingestion/document_intelligence/requirements.txt
```

For Tesseract:

```bash
pip install pytesseract
```

and install the Tesseract system binary separately for the target OS.

For PaddleOCR, install compatible `paddleocr` and `paddlepaddle` versions for the deployment environment.

For table fallback:

```bash
pip install pdfplumber
```

## 7. Environment variables

See `.env.example`:

```text
NWIS_DI_OCR_ENGINE=none|tesseract|paddleocr
NWIS_DI_OCR_LANG=eng
NWIS_DI_MIN_NATIVE_CHARS=20
NWIS_DI_DPI=200
NWIS_DI_MAX_FILE_SIZE_MB=100
```

No credentials or secrets are required by this module.

## 8. Unit tests

From the NWIS repository root:

```bash
pytest ingestion/document_intelligence/tests -q
```

The package currently passes all included tests. Tests cover native extraction, OCR fallback using a fake adapter, image validation, invalid-file validation, and output-contract serialization.

## 9. Example input

```text
DDR_OIL-WELL-001.pdf
```

The included sample is intentionally synthetic and is **NOT real OIL data**.

## 10. Example output

```json
{
  "document_id": "DOC-TEST-001",
  "file_name": "DDR_OIL-WELL-001.pdf",
  "well_id": "OIL-WELL-001",
  "document_type": "DDR",
  "pages": [
    {
      "page_number": 1,
      "text": "DAILY DRILLING REPORT...",
      "text_extraction_method": "native",
      "has_selectable_text": true,
      "provenance": {
        "document_id": "DOC-TEST-001",
        "file_name": "DDR_OIL-WELL-001.pdf",
        "page_number": 1,
        "section": null,
        "source_type": "DDR"
      }
    }
  ],
  "sections": [],
  "tables": [],
  "metadata": {
    "title": "DDR_OIL-WELL-001",
    "well_id": "OIL-WELL-001",
    "document_type": "DDR",
    "report_date": "2026-09-01",
    "operator": null,
    "source_type": "DDR"
  }
}
```

## 11. Integration instructions

1. Copy the `ingestion/document_intelligence` directory into the NWIS repository.
2. Install its requirements.
3. Select an OCR backend in the deployment environment.
4. Call `create_pipeline()` from an ingestion worker/API endpoint.
5. Pass `StructuredDocument.model_dump(mode="json")` to the NLP/RAG module.
6. Downstream modules should depend on `models.StructuredDocument` or its JSON contract, not internal OCR/PyMuPDF objects.

Example:

```python
from ingestion.document_intelligence.factory import create_pipeline

pipeline = create_pipeline()
document = pipeline.process("/data/incoming/report.pdf")
payload = document.model_dump(mode="json")
# send payload to the NLP/RAG ingestion boundary
```

## 12. Known limitations

- Metadata extraction is intentionally conservative and regex-based.
- Section segmentation is heuristic; it is not an LLM/semantic classifier.
- OCR accuracy depends on document quality and installed OCR models.
- Table extraction depends on PDF layout; complex scanned tables generally need OCR/table-specific processing in a future adapter.
- The module does not persist documents to PostgreSQL/PostGIS or Qdrant.
- No real OIL data is included.

## 13. Files created/modified

Created only under `ingestion/document_intelligence/`; no existing NWIS scaffold files were modified.
