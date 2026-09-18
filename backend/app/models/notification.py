from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NotificationConfig(Base):
    __tablename__ = "notification_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    webhook_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    min_match_score: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notification_config")
