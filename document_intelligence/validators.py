"""Input file validation utilities."""
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024


def validate_file(path: str | Path, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> Path:
    """Validate that *path* exists, is a regular file, and has a supported type."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Document does not exist: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Document path is not a file: {file_path}")
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported document type: {file_path.suffix or '<none>'}")
    size = file_path.stat().st_size
    if size == 0:
        raise ValueError("Document is empty")
    if size > max_size_bytes:
        raise ValueError(f"Document exceeds maximum size of {max_size_bytes} bytes")
    return file_path
