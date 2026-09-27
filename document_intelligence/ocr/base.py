"""OCR adapter interface."""
from abc import ABC, abstractmethod
from PIL import Image


class OCRAdapter(ABC):
    """Interface implemented by OCR engines."""

    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """Return text recognized from an image."""
        raise NotImplementedError
