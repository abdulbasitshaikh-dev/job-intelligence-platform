from app.database import Base
from app.models.application import ApplicationStatus, JobApplication
from app.models.job import EmploymentType, Job, WorkMode
from app.models.notification import NotificationConfig, NotificationLog
from app.models.saved_job import SavedJob
from app.models.source import ScraperRun, ScraperRunStatus, Source, SourceType
from app.models.user import JobPreference, User

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
    "NotificationLog",
]
