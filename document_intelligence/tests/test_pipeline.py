from pathlib import Path
import fitz
import pytest

from document_intelligence import DocumentIntelligencePipeline
from document_intelligence.validators import validate_file


SAMPLE_DIR = Path(__file__).parent / "sample_documents"


def make_text_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "DAILY DRILLING REPORT\nWell ID: OIL-WELL-001\nDate: 2026-09-01\n\nDRILLING PARAMETERS\nDepth: 2500 m\nROP: 12 m/hr")
    doc.save(path)
    doc.close()


def test_native_text_pdf(tmp_path):
    pdf = tmp_path / "DDR_OIL-WELL-001.pdf"
    make_text_pdf(pdf)
    result = DocumentIntelligencePipeline().process(pdf, document_id="DOC-TEST-001")
    assert result.document_id == "DOC-TEST-001"
    assert result.document_type == "DDR"
    assert result.well_id == "OIL-WELL-001"
    assert result.pages[0].has_selectable_text is True
    assert result.pages[0].text_extraction_method == "native"
    assert result.pages[0].provenance.page_number == 1
    assert result.sections


def test_ocr_fallback_is_called(tmp_path):
    pdf = tmp_path / "scanned.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(pdf)
    doc.close()

    class FakeOCR:
        def extract_text(self, image):
            return "WELL COMPLETION REPORT\nWell ID: OIL-WELL-002"

    result = DocumentIntelligencePipeline(ocr_adapter=FakeOCR(), min_native_chars=20).process(pdf)
    assert result.pages[0].text_extraction_method == "ocr"
    assert result.pages[0].has_selectable_text is False
    assert "WELL COMPLETION" in result.pages[0].text
    assert result.document_type == "WCR"
    assert result.well_id == "OIL-WELL-002"


def test_image_requires_ocr(tmp_path):
    from PIL import Image
    image_path = tmp_path / "scan.png"
    Image.new("RGB", (100, 100), "white").save(image_path)
    with pytest.raises(ValueError, match="OCR adapter"):
        DocumentIntelligencePipeline().process(image_path)


def test_invalid_file(tmp_path):
    path = tmp_path / "bad.txt"
    path.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported"):
        validate_file(path)
