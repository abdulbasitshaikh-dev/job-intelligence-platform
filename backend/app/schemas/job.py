from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.job import EmploymentType, WorkMode


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    source_name: Optional[str] = None
    external_id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    canonical_url: str
    employment_type: EmploymentType
    work_mode: WorkMode
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str
    posted_at: Optional[datetime] = None
    first_seen_at: datetime
    last_seen_at: datetime
    is_active: bool
    dedupe_hash: str

    # Optional dynamic match score field if calculated for context
    match_score: Optional[int] = None
    match_reasons: Optional[List[str]] = None
    is_saved: Optional[bool] = False
    application_status: Optional[str] = None


class JobSearchFilter(BaseModel):
    query: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[WorkMode] = None
    employment_type: Optional[EmploymentType] = None
    source_id: Optional[int] = None
    is_active: Optional[bool] = True
    min_salary: Optional[float] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class MatchReason(BaseModel):
    category: str
    points: int
    description: str


class MatchScoreResponse(BaseModel):
    job_id: int
    user_id: int
    total_score: int
    reasons: List[MatchReason]
