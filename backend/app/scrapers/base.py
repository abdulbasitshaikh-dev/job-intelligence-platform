from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.models.job import EmploymentType, WorkMode


class RawJobData(BaseModel):
    external_id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    salary_text: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = "USD"
    posted_at: Optional[datetime] = None
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class NormalizedJobData(BaseModel):
    source_id: int
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
    currency: str = "USD"
    posted_at: Optional[datetime] = None
    first_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    dedupe_hash: str
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class BaseScraper(ABC):
    """Abstract base class for all job source scrapers."""

    def __init__(self, source_id: int, base_url: str, config: Dict[str, Any], rate_limit_delay: float = 1.5):
        self.source_id = source_id
        self.base_url = base_url
        self.config = config
        self.rate_limit_delay = rate_limit_delay

    @abstractmethod
    async def fetch(self) -> List[Any]:
        """Fetch raw content or items from external source."""
        pass

    @abstractmethod
    def parse(self, raw_item: Any) -> RawJobData:
        """Parse raw fetched item into structured RawJobData."""
        pass

    @abstractmethod
    def normalize(self, raw_job: RawJobData) -> NormalizedJobData:
        """Transform RawJobData into canonical NormalizedJobData."""
        pass

    async def run(self) -> List[NormalizedJobData]:
        """Execute full fetch -> parse -> normalize pipeline safely."""
        raw_items = await self.fetch()
        normalized_jobs: List[NormalizedJobData] = []
        for item in raw_items:
            try:
                parsed = self.parse(item)
                normalized = self.normalize(parsed)
                normalized_jobs.append(normalized)
            except Exception as e:
                # Log item parsing/normalization error without failing entire batch
                continue
        return normalized_jobs
