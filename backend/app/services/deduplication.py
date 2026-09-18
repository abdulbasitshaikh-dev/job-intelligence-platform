from datetime import datetime, timezone
from typing import Tuple

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.scrapers.base import NormalizedJobData


class DeduplicationService:
    """Multi-tiered job deduplication service to prevent duplicate database records."""

    @staticmethod
    async def process_job(db: AsyncSession, item: NormalizedJobData) -> Tuple[Job, bool]:
        """
        Process normalized job item.
        Returns: Tuple[Job, is_created (True if new, False if updated duplicate)]
        """
        now = datetime.now(timezone.utc)

        # 1. Lookup by dedupe_hash OR (source_id, external_id) OR canonical_url
        stmt = select(Job).where(
            or_(
                Job.dedupe_hash == item.dedupe_hash,
                (Job.source_id == item.source_id) & (Job.external_id == item.external_id),
                Job.canonical_url == item.canonical_url,
            )
        )
        result = await db.execute(stmt)
        existing_job = result.scalars().first()

        if existing_job:
            # Update last_seen_at and mark active
            existing_job.last_seen_at = now
            existing_job.is_active = True
            await db.flush()
            return existing_job, False
        else:
            # Create new canonical job
            new_job = Job(
                source_id=item.source_id,
                external_id=item.external_id,
                title=item.title,
                company=item.company,
                location=item.location,
                description=item.description,
                url=item.url,
                canonical_url=item.canonical_url,
                employment_type=item.employment_type,
                work_mode=item.work_mode,
                salary_min=item.salary_min,
                salary_max=item.salary_max,
                currency=item.currency,
                posted_at=item.posted_at,
                first_seen_at=now,
                last_seen_at=now,
                is_active=True,
                dedupe_hash=item.dedupe_hash,
                raw_data=item.raw_data,
            )
            db.add(new_job)
            await db.flush()
            return new_job, True
