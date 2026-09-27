"""Factories for optional storage backends."""
from .config import get_settings
from .storage import LocalObjectStorage, S3ObjectStorage, ObjectStorage


def get_object_storage() -> ObjectStorage:
    """Create the configured object-storage adapter."""
    s = get_settings()
    if s.object_storage_backend.lower() == "s3":
        return S3ObjectStorage(s.s3_bucket, s.s3_endpoint_url, s.s3_region, s.s3_access_key_id, s.s3_secret_access_key)
    if s.object_storage_backend.lower() == "local":
        return LocalObjectStorage(s.object_storage_local_path)
    raise ValueError(f"Unsupported OBJECT_STORAGE_BACKEND: {s.object_storage_backend}")
