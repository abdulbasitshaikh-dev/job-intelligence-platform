from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.application import ApplicationStatus
from app.schemas.job import JobResponse


class JobApplicationCreate(BaseModel):
    job_id: int
    status: ApplicationStatus = ApplicationStatus.INTERESTED
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None


class JobApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None


class JobApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    job_id: int
    status: ApplicationStatus
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    job: Optional[JobResponse] = None
