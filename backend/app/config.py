from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings for the NWIS API gateway."""

    app_name: str = "NWIS Backend API"
    api_version: str = "v1"
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"
    database_url: str = "postgresql+psycopg://nwis:nwis@localhost:5432/nwis"
    enable_database: bool = False
    service_mode: str = "mock"
    max_page_size: int = 100
    nwis_package_root: str = ""
    risk_model_artifact_dir: str = "./artifacts/risk_model"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="NWIS_", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
