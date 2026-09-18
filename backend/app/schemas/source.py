from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.source import ScraperRunStatus, SourceType


class SourceBase(BaseModel):
    name: str = Field(..., max_length=150)
    base_url: str = Field(...)
    source_type: SourceType = SourceType.API
    scraper_type: str = Field(..., description="Key identifier for scraper implementation class")
    enabled: bool = True
    configuration: Dict[str, Any] = Field(default_factory=dict)
    rate_limit_delay: float = Field(1.5, ge=0.1, le=60.0)


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    source_type: Optional[SourceType] = None
    scraper_type: Optional[str] = None
    enabled: Optional[bool] = None
    configuration: Optional[Dict[str, Any]] = None
    rate_limit_delay: Optional[float] = None


class SourceResponse(SourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_run_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    consecutive_failures: int = 0
    created_at: datetime
    updated_at: datetime


class ScraperRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: ScraperRunStatus
    pages_fetched: int
    jobs_found: int
    jobs_created: int
    duplicates_found: int
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
