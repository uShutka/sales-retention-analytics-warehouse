from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "local"
    project_name: str = "Sales & Retention Analytics Warehouse"
    data_dir: Path = Path("data/raw")
    database_url: str = "postgresql+psycopg://analytics:analytics@postgres:5432/sales_warehouse"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]
