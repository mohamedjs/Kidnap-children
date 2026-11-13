from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV = Path(__file__).resolve().parents[4] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(str(ROOT_ENV), ".env"), extra="ignore")

    app_env: str = "development"
    api_port: int = 4100
    database_url: str
    jwt_secret: str
    jwt_ttl_minutes: int = 720
    cors_origins: str = "http://localhost:3100"
    public_web_url: str = "http://localhost:3100"

    s3_endpoint: str = ""
    s3_public_endpoint: str = ""
    s3_region: str = "us-east-1"
    s3_bucket: str = "kidnap-media"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_force_path_style: bool = True
    s3_allowed_origins: str = ""
    upload_url_ttl_seconds: int = 300
    download_url_ttl_seconds: int = 300

    admin_seed_email: str = "admin@demo.local"
    admin_seed_password: str = ""

    n8n_webhook_url: str = ""
    n8n_webhook_secret: str = ""
    google_maps_api_key: str = ""

    worker_poll_seconds: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
