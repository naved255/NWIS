"""Optional Tesseract OCR adapter."""
from PIL import Image
from .base import OCRAdapter


class TesseractOCR(OCRAdapter):
    """OCR adapter using pytesseract and a local Tesseract installation."""

    def __init__(self, lang: str = "eng", config: str = "") -> None:
        try:
            import pytesseract
        except ImportError as exc:
            raise ImportError("Install pytesseract to use TesseractOCR") from exc
        self._pytesseract = pytesseract
        self.lang = lang
        self.config = config

    def extract_text(self, image: Image.Image) -> str:
        """Run Tesseract on a PIL image."""
        return self._pytesseract.image_to_string(image, lang=self.lang, config=self.config).strip()
