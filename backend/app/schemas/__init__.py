from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.user import (
    UserRegister,
    UserLogin,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    UserUpdate,
)
from app.schemas.preference import (
    JobPreferenceCreate,
    JobPreferenceUpdate,
    JobPreferenceResponse,
)
from app.schemas.source import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    ScraperRunResponse,
)
from app.schemas.job import (
    JobResponse,
    JobSearchFilter,
    MatchReason,
    MatchScoreResponse,
)
from app.schemas.application import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
)
from app.schemas.notification import (
    NotificationConfigUpdate,
    NotificationConfigResponse,
)

__all__ = [
    "PaginatedResponse",
    "MessageResponse",
    "UserRegister",
    "UserLogin",
    "RefreshTokenRequest",
    "TokenResponse",
    "UserResponse",
    "UserUpdate",
    "JobPreferenceCreate",
    "JobPreferenceUpdate",
    "JobPreferenceResponse",
    "SourceCreate",
    "SourceUpdate",
    "SourceResponse",
    "ScraperRunResponse",
    "JobResponse",
    "JobSearchFilter",
    "MatchReason",
    "MatchScoreResponse",
    "JobApplicationCreate",
    "JobApplicationUpdate",
    "JobApplicationResponse",
    "NotificationConfigUpdate",
    "NotificationConfigResponse",
]
