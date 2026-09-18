from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationConfigUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    min_match_score: Optional[int] = Field(None, ge=0, le=100)


class NotificationConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    email_notifications: bool
    webhook_url: Optional[str] = None
    min_match_score: int
    created_at: datetime
    updated_at: datetime
