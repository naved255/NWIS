# NWIS Document Intelligence

Independent document-processing pipeline for historical drilling documents (WCR, DDR, scanned PDFs, images, operational reports and completion reports).

## Flow

`validation -> native PDF extraction -> OCR fallback -> page segmentation -> table extraction -> text cleaning -> metadata extraction -> StructuredDocument`

No RAG, embeddings, semantic search or predictive ML are performed here.

## Quick start

```bash
pip install -r ingestion/document_intelligence/requirements.txt
```

For OCR choose one backend:

```python
from ingestion.document_intelligence import DocumentIntelligencePipeline
from ingestion.document_intelligence.ocr.tesseract_adapter import TesseractOCR

pipeline = DocumentIntelligencePipeline(ocr_adapter=TesseractOCR())
doc = pipeline.process("DDR_001.pdf")
print(doc.model_dump_json(indent=2))
```

For PaddleOCR, replace the adapter with `PaddleOCREngine()`.

## Contract

The output is a Pydantic `StructuredDocument` with `document_id`, `file_name`, `well_id`, `document_type`, `pages`, `sections`, `tables`, and `metadata`. Every page, section and table carries provenance: `document_id`, `file_name`, `page_number`, `section`, and `source_type` (section may be null for page/table-level records).

## Integration

The NLP/RAG modules should consume `StructuredDocument.model_dump()` or `model_dump_json()` and should not import internal extraction classes. The pipeline can be instantiated inside a FastAPI service, background worker, or batch job.

## Limitations

- Metadata extraction is deterministic regex-based extraction, not semantic entity extraction.
- Section detection is heuristic based on heading-like lines.
- OCR quality depends on the installed OCR engine and language models.
- Table extraction uses PyMuPDF's table API when available; a future adapter can add pdfplumber/Camelot without changing the output contract.
- PDFs with no selectable text and no configured OCR adapter are reported with `text_extraction_method="none"` rather than silently fabricating text.

## Environment configuration

Copy `.env.example` into the deployment environment (do not commit secrets; this module has no secret variables).

- `NWIS_DI_OCR_ENGINE`: `none`, `tesseract`, or `paddleocr`.
- `NWIS_DI_OCR_LANG`: OCR language; `eng` is the Tesseract default.
- `NWIS_DI_MIN_NATIVE_CHARS`: minimum extracted native characters before OCR fallback (default `20`).
- `NWIS_DI_DPI`: PDF render DPI for OCR (default `200`).
- `NWIS_DI_MAX_FILE_SIZE_MB`: documented input-size limit (default `100`).

Use `create_pipeline()` from `factory.py` to construct the pipeline from these settings.
