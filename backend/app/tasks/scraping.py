import asyncio
import time
from datetime import datetime, timezone

from sqlalchemy import select

from app.celery_app import celery_app
from app.core.logging import logger
from app.database import SyncSessionLocal
from app.models.source import ScraperRun, ScraperRunStatus, Source
from app.scrapers.sources.scraper_registry import get_scraper_class


async def _async_scrape_source(source_id: int) -> dict:
    start_time = time.time()
    now = datetime.now(timezone.utc)

    # Use SyncSession wrapped for async task execution
    with SyncSessionLocal() as session:
        source = session.get(Source, source_id)
        if not source or not source.enabled:
            return {"status": "SKIPPED", "reason": "Source disabled or not found"}

        # Create ScraperRun entry
        run = ScraperRun(
            source_id=source.id,
            started_at=now,
            status=ScraperRunStatus.IN_PROGRESS,
            pages_fetched=1,
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        try:
            scraper_cls = get_scraper_class(source.scraper_type)
            scraper = scraper_cls(
                source_id=source.id,
                base_url=source.base_url,
                config=source.configuration or {},
                rate_limit_delay=float(source.rate_limit_delay or 1.5),
            )

            # Execute scraper fetch/parse/normalize pipeline
            normalized_jobs = await scraper.run()

            jobs_found = len(normalized_jobs)
            jobs_created = 0
            duplicates_found = 0

            # Deduplicate and save using async session adapter or sync logic
            # Standard sync loop for DB insertion
            for job_data in normalized_jobs:
                from app.models.job import Job
                stmt = select(Job).where(
                    (Job.dedupe_hash == job_data.dedupe_hash) |
                    ((Job.source_id == job_data.source_id) & (Job.external_id == job_data.external_id))
                )
                existing = session.execute(stmt).scalars().first()
                if existing:
                    existing.last_seen_at = now
                    existing.is_active = True
                    duplicates_found += 1
                else:
                    new_job = Job(
                        source_id=job_data.source_id,
                        external_id=job_data.external_id,
                        title=job_data.title,
                        company=job_data.company,
                        location=job_data.location,
                        description=job_data.description,
                        url=job_data.url,
                        canonical_url=job_data.canonical_url,
                        employment_type=job_data.employment_type,
                        work_mode=job_data.work_mode,
                        salary_min=job_data.salary_min,
                        salary_max=job_data.salary_max,
                        currency=job_data.currency,
                        posted_at=job_data.posted_at,
                        first_seen_at=now,
                        last_seen_at=now,
                        is_active=True,
                        dedupe_hash=job_data.dedupe_hash,
                        raw_data=job_data.raw_data,
                    )
                    session.add(new_job)
                    jobs_created += 1

            duration = round(time.time() - start_time, 2)

            # Update ScraperRun & Source metrics
            run.status = ScraperRunStatus.SUCCESS
            run.completed_at = datetime.now(timezone.utc)
            run.jobs_found = jobs_found
            run.jobs_created = jobs_created
            run.duplicates_found = duplicates_found
            run.duration_seconds = duration

            source.last_run_at = now
            source.last_success_at = now
            source.consecutive_failures = 0

            session.commit()
            logger.info(
                "Source scraped successfully",
                source_name=source.name,
                jobs_found=jobs_found,
                jobs_created=jobs_created,
                duplicates=duplicates_found,
                duration=duration,
            )
            return {
                "source_id": source.id,
                "status": "SUCCESS",
                "jobs_created": jobs_created,
                "duplicates": duplicates_found,
            }

        except Exception as e:
            duration = round(time.time() - start_time, 2)
            error_msg = str(e)

            run.status = ScraperRunStatus.FAILED
            run.completed_at = datetime.now(timezone.utc)
            run.error_message = error_msg
            run.duration_seconds = duration

            source.last_run_at = now
            source.last_failure_at = now
            source.consecutive_failures += 1

            session.commit()
            logger.error("Scraper execution failed", source_id=source_id, error=error_msg)
            return {"source_id": source_id, "status": "FAILED", "error": error_msg}


@celery_app.task(name="app.tasks.scraping.scrape_source_task", bind=True, max_retries=3, default_retry_delay=60)
def scrape_source_task(self, source_id: int):
    """Celery task wrapper to execute scraper in async event loop."""
    return asyncio.run(_async_scrape_source(source_id))


@celery_app.task(name="app.tasks.scraping.scrape_all_sources_task")
def scrape_all_sources_task():
    """Celery task to trigger scraping for all enabled sources."""
    with SyncSessionLocal() as session:
        sources = session.execute(select(Source).where(Source.enabled == True)).scalars().all()
        results = []
        for src in sources:
            res = scrape_source_task.delay(src.id)
            results.append(res.id)
        return {"dispatched_tasks": len(results), "source_ids": [s.id for s in sources]}
