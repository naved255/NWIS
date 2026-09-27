# NWIS Document Intelligence Module Contract

## Input
- PDF, PNG, JPG/JPEG, TIFF, BMP, WEBP.
- PDF may contain selectable text or be image/scanned content.

## Output
`StructuredDocument` from `models.py`.

### Required provenance
Every extracted page, section and table contains:
- `document_id`
- `file_name`
- `page_number`
- `section`
- `source_type`

## Downstream contract
NLP/RAG should consume only the public `StructuredDocument` object or its JSON representation. Do not depend on PyMuPDF page objects, OCR engine objects, or internal segmentation functions.

## Failure behavior
- Invalid/unsupported file: raises `ValueError`/`FileNotFoundError`.
- Image without OCR adapter: raises `ValueError`.
- PDF page without selectable text and without OCR: page is returned with `text_extraction_method="none"` and empty/native text.
- OCR exception: logged and page is returned with empty text; the rest of the document continues processing.
