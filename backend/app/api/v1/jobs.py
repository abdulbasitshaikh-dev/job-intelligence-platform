import math
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user
from app.core.exceptions import DuplicateResourceException, NotFoundException
from app.database import get_db
from app.models.job import EmploymentType, Job, WorkMode
from app.models.saved_job import SavedJob
from app.models.application import JobApplication
from app.models.user import User, JobPreference
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.job import JobResponse
from app.services.matching import MatchingService

router = APIRouter(prefix="/jobs", tags=["Jobs & Feed"])


@router.get("", response_model=PaginatedResponse[JobResponse])
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    work_mode: Optional[WorkMode] = None,
    employment_type: Optional[EmploymentType] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve paginated job feed, annotated with match score & user save/application status."""
    preference = None
    saved_ids: set = set()
    applications: dict = {}

    if current_user:
        # Get user preferences
        pref_stmt = select(JobPreference).where(JobPreference.user_id == current_user.id)
        preference = (await db.execute(pref_stmt)).scalars().first()

        # Get user saved job IDs and applications
        saved_stmt = select(SavedJob.job_id).where(SavedJob.user_id == current_user.id)
        saved_ids = set((await db.execute(saved_stmt)).scalars().all())

        app_stmt = select(JobApplication).where(JobApplication.user_id == current_user.id)
        applications = {app.job_id: app.status.value for app in (await db.execute(app_stmt)).scalars().all()}

    # Query active jobs
    query = select(Job).where(Job.is_active == True)
    if work_mode:
        query = query.where(Job.work_mode == work_mode)
    if employment_type:
        query = query.where(Job.employment_type == employment_type)

    # Count total
    total_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_stmt)).scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.order_by(Job.posted_at.desc(), Job.id.desc()).offset(offset).limit(page_size)
    jobs = (await db.execute(query)).scalars().all()

    # Annotate jobs
    items: List[JobResponse] = []
    for j in jobs:
        resp = JobResponse.model_validate(j)
        if preference:
            score_res = MatchingService.calculate_match_score(j, preference)
            resp.match_score = score_res.total_score
            resp.match_reasons = [r.description for r in score_res.reasons]
        resp.is_saved = j.id in saved_ids
        resp.application_status = applications.get(j.id)
        items.append(resp)

    pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(items=items, page=page, page_size=page_size, total=total, pages=pages)


@router.get("/search", response_model=PaginatedResponse[JobResponse])
async def search_jobs(
    q: Optional[str] = Query(None, description="Search keyword in title, company, or description"),
    company: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[WorkMode] = None,
    employment_type: Optional[EmploymentType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Search and filter jobs dynamically."""
    query = select(Job).where(Job.is_active == True)

    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                Job.title.ilike(search_pattern),
                Job.company.ilike(search_pattern),
                Job.description.ilike(search_pattern),
                Job.location.ilike(search_pattern),
            )
        )
    if company:
        query = query.where(Job.company.ilike(f"%{company.strip()}%"))
    if location:
        query = query.where(Job.location.ilike(f"%{location.strip()}%"))
    if work_mode:
        query = query.where(Job.work_mode == work_mode)
    if employment_type:
        query = query.where(Job.employment_type == employment_type)

    total_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_stmt)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(Job.posted_at.desc()).offset(offset).limit(page_size)
    jobs = (await db.execute(query)).scalars().all()

    pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(
        items=[JobResponse.model_validate(j) for j in jobs],
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )


@router.get("/saved/me", response_model=List[JobResponse])
async def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all saved jobs for current user."""
    stmt = (
        select(Job)
        .join(SavedJob, SavedJob.job_id == Job.id)
        .where(SavedJob.user_id == current_user.id)
        .order_by(SavedJob.saved_at.desc())
    )
    jobs = (await db.execute(stmt)).scalars().all()
    items = []
    for j in jobs:
        resp = JobResponse.model_validate(j)
        resp.is_saved = True
        items.append(resp)
    return items


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_detail(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed view of a single job opportunity."""
    job = await db.get(Job, job_id)
    if not job:
        raise NotFoundException(detail="Job not found")

    resp = JobResponse.model_validate(job)
    
    pref_stmt = select(JobPreference).where(JobPreference.user_id == current_user.id)
    preference = (await db.execute(pref_stmt)).scalars().first()
    if preference:
        score_res = MatchingService.calculate_match_score(job, preference)
        resp.match_score = score_res.total_score
        resp.match_reasons = [r.description for r in score_res.reasons]

    saved_stmt = select(SavedJob).where((SavedJob.user_id == current_user.id) & (SavedJob.job_id == job_id))
    resp.is_saved = (await db.execute(saved_stmt)).scalars().first() is not None

    return resp


@router.post("/{job_id}/save", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def save_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a job opportunity to user's saved jobs list."""
    job = await db.get(Job, job_id)
    if not job:
        raise NotFoundException(detail="Job not found")

    stmt = select(SavedJob).where((SavedJob.user_id == current_user.id) & (SavedJob.job_id == job_id))
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise DuplicateResourceException(detail="Job is already saved")

    saved = SavedJob(user_id=current_user.id, job_id=job_id)
    db.add(saved)
    await db.commit()
    return MessageResponse(message="Job saved successfully")


@router.delete("/{job_id}/save", response_model=MessageResponse)
async def unsave_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a job from user's saved list."""
    stmt = select(SavedJob).where((SavedJob.user_id == current_user.id) & (SavedJob.job_id == job_id))
    saved = (await db.execute(stmt)).scalars().first()
    if not saved:
        raise NotFoundException(detail="Saved job entry not found")

    await db.delete(saved)
    await db.commit()
    return MessageResponse(message="Job unsaved successfully")


@router.post("/sync", summary="Trigger live real-time ingestion from active job sources")
async def sync_live_jobs(
    db: AsyncSession = Depends(get_db),
):
    """Trigger live real-time ingestion directly from active job sources (RemoteOK, Arbeitnow, etc.)."""
    from datetime import datetime, timezone
    from app.models.source import Source
    from app.scrapers.sources.scraper_registry import get_scraper_class
    from app.core.logging import logger

    stmt = select(Source).where(Source.enabled == True)
    sources = (await db.execute(stmt)).scalars().all()
    if not sources:
        return {"status": "no_sources", "message": "No enabled sources configured", "new_jobs": 0, "total_jobs": 0}

    now = datetime.now(timezone.utc)
    existing_hashes = set((await db.execute(select(Job.dedupe_hash))).scalars().all())
    existing_keys = set((await db.execute(select(Job.source_id, Job.external_id))).all())
    
    total_found = 0
    total_added = 0
    sources_synced = []

    for src in sources:
        try:
            scraper_cls = get_scraper_class(src.scraper_type)
            scraper = scraper_cls(
                source_id=src.id,
                base_url=src.base_url,
                config=src.configuration or {},
                rate_limit_delay=float(src.rate_limit_delay or 1.5),
            )
            jobs = await scraper.run()
            total_found += len(jobs)
            sources_synced.append(src.name)

            for j in jobs:
                if j.dedupe_hash in existing_hashes or (j.source_id, j.external_id) in existing_keys:
                    continue
                existing_hashes.add(j.dedupe_hash)
                existing_keys.add((j.source_id, j.external_id))

                job_record = Job(
                    source_id=j.source_id,
                    external_id=j.external_id,
                    title=j.title,
                    company=j.company,
                    location=j.location,
                    description=j.description,
                    url=j.url,
                    canonical_url=j.canonical_url,
                    employment_type=j.employment_type,
                    work_mode=j.work_mode,
                    salary_min=j.salary_min,
                    salary_max=j.salary_max,
                    currency=j.currency,
                    posted_at=j.posted_at,
                    first_seen_at=now,
                    last_seen_at=now,
                    is_active=True,
                    dedupe_hash=j.dedupe_hash,
                    raw_data=j.raw_data,
                )
                db.add(job_record)
                total_added += 1

            src.last_run_at = now
            src.last_success_at = now
            src.consecutive_failures = 0
        except Exception as e:
            logger.error("Live sync failed for source", source=src.name, error=str(e))
            src.last_failure_at = now
            src.consecutive_failures += 1

    await db.commit()
    total_active = (await db.execute(select(func.count(Job.id)).where(Job.is_active == True))).scalar() or 0

    return {
        "status": "success",
        "message": f"Synced {len(sources_synced)} sources. Found {total_found} live jobs, added {total_added} new unique jobs.",
        "sources": sources_synced,
        "new_jobs": total_added,
        "total_active_jobs": total_active,
    }

