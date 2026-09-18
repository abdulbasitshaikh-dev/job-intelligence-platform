from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class JobPreferenceCreate(BaseModel):
    keywords: List[str] = Field(default_factory=list, json_schema_extra={"example": ["Python", "FastAPI", "Backend"]})
    locations: List[str] = Field(default_factory=list, json_schema_extra={"example": ["Pakistan", "Karachi", "Remote"]})
    employment_types: List[str] = Field(default_factory=list, json_schema_extra={"example": ["Full-time", "Contract"]})
    work_modes: List[str] = Field(default_factory=list, json_schema_extra={"example": ["Remote", "Hybrid"]})
    min_salary: Optional[float] = Field(None, ge=0)
    max_salary: Optional[float] = Field(None, ge=0)
    currency: str = Field("USD", max_length=10)


class JobPreferenceUpdate(BaseModel):
    keywords: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    employment_types: Optional[List[str]] = None
    work_modes: Optional[List[str]] = None
    min_salary: Optional[float] = Field(None, ge=0)
    max_salary: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)


class JobPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    keywords: List[str]
    locations: List[str]
    employment_types: List[str]
    work_modes: List[str]
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str
    created_at: datetime
    updated_at: datetime
