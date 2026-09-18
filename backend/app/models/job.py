from datetime import datetime, timezone
from typing import List, Optional
import enum
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmploymentType(str, enum.Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    TEMPORARY = "Temporary"
    OTHER = "Other"


class WorkMode(str, enum.Enum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ON_SITE = "On-site"
    UNSPECIFIED = "Unspecified"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    
    employment_type: Mapped[EmploymentType] = mapped_column(
        SQLEnum(EmploymentType), default=EmploymentType.FULL_TIME, nullable=False, index=True
    )
    work_mode: Mapped[WorkMode] = mapped_column(
        SQLEnum(WorkMode), default=WorkMode.REMOTE, nullable=False, index=True
    )
    
    salary_min: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    dedupe_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

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
    source: Mapped["Source"] = relationship("Source", back_populates="jobs")
    saved_by_users: Mapped[List["SavedJob"]] = relationship(
        "SavedJob", back_populates="job", cascade="all, delete-orphan"
    )
    applications: Mapped[List["JobApplication"]] = relationship(
        "JobApplication", back_populates="job", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_source_external_id"),
        Index("idx_jobs_company_title", "company", "title"),
        Index("idx_jobs_posted_active", "posted_at", "is_active"),
    )
