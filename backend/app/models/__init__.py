from app.database import Base
from app.models.user import User, JobPreference
from app.models.source import Source, SourceType, ScraperRun, ScraperRunStatus
from app.models.job import Job, EmploymentType, WorkMode
from app.models.saved_job import SavedJob
from app.models.application import JobApplication, ApplicationStatus
from app.models.notification import NotificationConfig

__all__ = [
    "Base",
    "User",
    "JobPreference",
    "Source",
    "SourceType",
    "ScraperRun",
    "ScraperRunStatus",
    "Job",
    "EmploymentType",
    "WorkMode",
    "SavedJob",
    "JobApplication",
    "ApplicationStatus",
    "NotificationConfig",
]
