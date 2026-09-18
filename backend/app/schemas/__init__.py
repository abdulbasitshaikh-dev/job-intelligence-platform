from app.schemas.application import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
)
from app.schemas.common import MessageResponse, PaginatedResponse, PlatformStatsResponse
from app.schemas.job import (
    JobResponse,
    JobSearchFilter,
    MatchReason,
    MatchScoreResponse,
)
from app.schemas.notification import (
    NotificationConfigResponse,
    NotificationConfigUpdate,
)
from app.schemas.preference import (
    JobPreferenceCreate,
    JobPreferenceResponse,
    JobPreferenceUpdate,
)
from app.schemas.source import (
    ScraperRunResponse,
    SourceCreate,
    SourceResponse,
    SourceUpdate,
)
from app.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
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
    "PlatformStatsResponse",
]
