import json
from typing import List, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Job Intelligence Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # SECRET_KEY: in production, an explicit, strong random key MUST be configured.
    # In development/test, a fallback dev key is provided so tests and local dev operate smoothly.
    SECRET_KEY: str = "dev-insecure-secret-key-replace-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "jobuser"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "job_intelligence_db"
    DATABASE_URL: str = ""
    SYNC_DATABASE_URL: str = ""

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Scraping Settings
    SCRAPE_REQUEST_TIMEOUT: float = 15.0
    SCRAPE_REQUEST_DELAY: float = 1.5
    SCRAPE_MAX_PAGES: int = 5
    PLAYWRIGHT_HEADLESS: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    # Webhook & Notifications
    DEFAULT_WEBHOOK_URL: str = ""
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "notifications@jobintelligence.io"
    EMAILS_FROM_NAME: str = "Job Intelligence Platform"

    # Demo account seeding credentials (development only)
    SEED_ADMIN_PASSWORD: str = ""
    SEED_DEMO_PASSWORD: str = ""

    @model_validator(mode="after")
    def validate_and_assemble_settings(self) -> "Settings":
        env = (self.ENVIRONMENT or "development").lower()

        # Construct default database URLs if not explicitly provided
        pwd = self.POSTGRES_PASSWORD or ""
        auth = f"{self.POSTGRES_USER}:{pwd}@" if pwd else f"{self.POSTGRES_USER}@"
        host_port = f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}"
        db = self.POSTGRES_DB

        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql+asyncpg://{auth}{host_port}/{db}"
        if not self.SYNC_DATABASE_URL:
            self.SYNC_DATABASE_URL = f"postgresql+psycopg2://{auth}{host_port}/{db}"

        # Strict production enforcement
        if env == "production":
            insecure_markers = ("dev-insecure", "change-in-production", "replace-in-production")
            if not self.SECRET_KEY or any(m in self.SECRET_KEY.lower() for m in insecure_markers):
                raise ValueError(
                    "Production requires an explicitly configured, secure SECRET_KEY. "
                    "Do not use development defaults in production."
                )
            if not self.POSTGRES_PASSWORD:
                raise ValueError(
                    "Production requires an explicitly configured POSTGRES_PASSWORD."
                )

        return self


settings = Settings()
