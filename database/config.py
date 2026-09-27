"""Configuration for the NWIS persistent storage layer."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed storage settings."""

    database_url: str = "postgresql+psycopg://nwis:nwis@localhost:5432/nwis"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "nwis_document_chunks"
    object_storage_backend: str = "local"
    object_storage_local_path: str = "./data/objects"
    s3_endpoint_url: str | None = None
    s3_bucket: str = "nwis-documents"
    s3_region: str = "ap-south-1"
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
