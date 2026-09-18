from datetime import datetime, timezone
from typing import List, Optional
import enum
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SourceType(str, enum.Enum):
    HTML = "HTML"
    API = "API"
    BROWSER = "BROWSER"


class ScraperRunStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        SQLEnum(SourceType), default=SourceType.API, nullable=False
    )
    scraper_type: Mapped[str] = mapped_column(String(100), nullable=False)  # Class/adapter key
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    configuration: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    rate_limit_delay: Mapped[float] = mapped_column(Numeric(5, 2), default=1.5, nullable=False)
    
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

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
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="source", cascade="all, delete-orphan")
    runs: Mapped[List["ScraperRun"]] = relationship("ScraperRun", back_populates="source", cascade="all, delete-orphan")


class ScraperRun(Base):
    __tablename__ = "scraper_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ScraperRunStatus] = mapped_column(
        SQLEnum(ScraperRunStatus), default=ScraperRunStatus.IN_PROGRESS, nullable=False, index=True
    )
    pages_fetched: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicates_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)

    # Relationships
    source: Mapped["Source"] = relationship("Source", back_populates="runs")
