import json
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Job Intelligence Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "jobuser"
    POSTGRES_PASSWORD: str = "jobpassword"
    POSTGRES_DB: str = "job_intelligence_db"
    DATABASE_URL: str = "postgresql+asyncpg://jobuser:jobpassword@127.0.0.1:5432/job_intelligence_db"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://jobuser:jobpassword@127.0.0.1:5432/job_intelligence_db"

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
    DEFAULT_WEBHOOK_URL: str = "http://localhost:5678/webhook/job-events"
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "notifications@example.com"
    SMTP_PASSWORD: str = "secretpassword"
    EMAILS_FROM_EMAIL: str = "notifications@jobintelligence.io"
    EMAILS_FROM_NAME: str = "Job Intelligence Platform"


settings = Settings()
