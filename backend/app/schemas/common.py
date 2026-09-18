from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total: int = Field(..., ge=0, description="Total number of matching items")
    pages: int = Field(..., ge=0, description="Total number of pages")


class MessageResponse(BaseModel):
    message: str


class PlatformStatsResponse(BaseModel):
    active_jobs: int
    total_jobs: int
    configured_sources: int
    healthy_sources: int
    last_successful_sync: Optional[datetime] = None
    jobs_added_recently: int = 0

