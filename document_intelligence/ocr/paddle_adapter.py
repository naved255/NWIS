"""Optional PaddleOCR adapter."""
from PIL import Image
from .base import OCRAdapter


class PaddleOCREngine(OCRAdapter):
    """OCR adapter for PaddleOCR.

    PaddleOCR has changed constructor/result formats across major versions; this
    adapter deliberately normalizes the common v2/v3 output shapes.
    """

    def __init__(self, lang: str = "en", **kwargs) -> None:
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise ImportError("Install paddleocr and paddlepaddle to use PaddleOCREngine") from exc
        self._ocr = PaddleOCR(lang=lang, **kwargs)

    def extract_text(self, image: Image.Image) -> str:
        """Run PaddleOCR and flatten recognized lines into plain text."""
        import numpy as np
        result = self._ocr.predict(np.array(image)) if hasattr(self._ocr, "predict") else self._ocr.ocr(np.array(image), cls=True)
        texts: list[str] = []
        self._collect_texts(result, texts)
        return "\n".join(t for t in texts if t.strip())

    @classmethod
    def _collect_texts(cls, value, output: list[str]) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"rec_texts", "text", "texts"}:
                    if isinstance(item, str):
                        output.append(item)
                    elif isinstance(item, (list, tuple)):
                        output.extend(str(x) for x in item)
                else:
                    cls._collect_texts(item, output)
        elif isinstance(value, (list, tuple)):
            for item in value:
                # Paddle v2: [box, (text, score)]
                if isinstance(item, (list, tuple)) and len(item) >= 2 and isinstance(item[1], (list, tuple)) and item[1] and isinstance(item[1][0], str):
                    output.append(item[1][0])
                else:
                    cls._collect_texts(item, output)
