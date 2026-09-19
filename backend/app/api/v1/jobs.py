import math
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_superuser, get_current_user, get_optional_user
from app.core.exceptions import DuplicateResourceException, NotFoundException
from app.database import get_db
from app.models.application import JobApplication
from app.models.job import EmploymentType, Job, WorkMode
from app.models.saved_job import SavedJob
from app.models.source import Source
from app.models.user import JobPreference, User
from app.schemas.common import MessageResponse, PaginatedResponse, PlatformStatsResponse
from app.schemas.job import JobResponse
from app.services.matching import MatchingService

router = APIRouter(prefix="/jobs", tags=["Jobs & Feed"])


@router.get("/stats", response_model=PlatformStatsResponse, summary="Retrieve public platform statistics")
async def get_platform_stats(db: AsyncSession = Depends(get_db)):
    """Return live platform statistics: active job count, configured sources, and sync timestamp."""
    active_jobs = (await db.execute(select(func.count(Job.id)).where(Job.is_active == True))).scalar() or 0
    total_jobs = (await db.execute(select(func.count(Job.id)))).scalar() or 0
    configured_sources = (await db.execute(select(func.count(Source.id)).where(Source.enabled == True))).scalar() or 0
    healthy_sources = (
        await db.execute(
            select(func.count(Source.id)).where((Source.enabled == True) & (Source.consecutive_failures == 0))
        )
    ).scalar() or 0

    last_sync = (await db.execute(select(func.max(Source.last_success_at)))).scalar()

    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    recent_jobs = (
        await db.execute(select(func.count(Job.id)).where(Job.first_seen_at >= one_day_ago))
    ).scalar() or 0

    return PlatformStatsResponse(
        active_jobs=active_jobs,
        total_jobs=total_jobs,
        configured_sources=configured_sources,
        healthy_sources=healthy_sources,
        last_successful_sync=last_sync,
        jobs_added_recently=recent_jobs,
    )


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
        pref_stmt = select(JobPreference).where(JobPreference.user_id == current_user.id)
        preference = (await db.execute(pref_stmt)).scalars().first()

        saved_stmt = select(SavedJob.job_id).where(SavedJob.user_id == current_user.id)
        saved_ids = set((await db.execute(saved_stmt)).scalars().all())

        app_stmt = select(JobApplication).where(JobApplication.user_id == current_user.id)
        applications = {app.job_id: app.status.value for app in (await db.execute(app_stmt)).scalars().all()}

    # Query active jobs with eager-loaded source
    query = select(Job).options(selectinload(Job.source)).where(Job.is_active == True)
    if work_mode:
        query = query.where(Job.work_mode == work_mode)
    if employment_type:
        query = query.where(Job.employment_type == employment_type)

    total_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_stmt)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(Job.posted_at.desc(), Job.id.desc()).offset(offset).limit(page_size)
    jobs = (await db.execute(query)).scalars().all()

    items: List[JobResponse] = []
    for j in jobs:
        resp = JobResponse.model_validate(j)
        resp.source_name = j.source.name if j.source else "Public Source"
        if preference and MatchingService.has_meaningful_preferences(preference):
            score_res = MatchingService.calculate_match_score(j, preference)
            resp.match_score = score_res.total_score
            resp.match_reasons = [r.description for r in score_res.reasons]
        else:
            resp.match_score = None
            resp.match_reasons = []
        resp.is_saved = j.id in saved_ids
        resp.application_status = applications.get(j.id)
        items.append(resp)

    pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(items=items, page=page, page_size=page_size, total=total, pages=pages)


@router.get("/search", response_model=PaginatedResponse[JobResponse])
async def search_jobs(
    q: Optional[str] = Query(None, description="Search query ranked with title relevance"),
    company: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[WorkMode] = None,
    employment_type: Optional[EmploymentType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search jobs with title-weighted relevance ranking.
    Title matches rank strictly higher than descriptions or company mentions.
    """
    preference = None
    saved_ids: set = set()
    applications: dict = {}

    if current_user:
        pref_stmt = select(JobPreference).where(JobPreference.user_id == current_user.id)
        preference = (await db.execute(pref_stmt)).scalars().first()

        saved_stmt = select(SavedJob.job_id).where(SavedJob.user_id == current_user.id)
        saved_ids = set((await db.execute(saved_stmt)).scalars().all())

        app_stmt = select(JobApplication).where(JobApplication.user_id == current_user.id)
        applications = {app.job_id: app.status.value for app in (await db.execute(app_stmt)).scalars().all()}

    query = select(Job).options(selectinload(Job.source)).where(Job.is_active == True)
    order_clauses = []

    if q and q.strip():
        term = q.strip()
        exact_lower = term.lower()
        contains_pattern = f"%{exact_lower}%"

        # SQL Relevance weighting (Title receives strongest relevance)
        relevance_score = case(
            (func.lower(Job.title) == exact_lower, 100),
            (func.lower(Job.title).like(f"{exact_lower}%"), 85),
            (func.lower(Job.title).like(contains_pattern), 70),
            (func.lower(Job.company).like(contains_pattern), 40),
            (func.lower(Job.location).like(contains_pattern), 25),
            (func.lower(Job.description).like(contains_pattern), 10),
            else_=0,
        )

        query = query.where(
            or_(
                Job.title.ilike(contains_pattern),
                Job.company.ilike(contains_pattern),
                Job.description.ilike(contains_pattern),
                Job.location.ilike(contains_pattern),
            )
        )
        order_clauses.append(relevance_score.desc())

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

    order_clauses.extend([Job.posted_at.desc(), Job.id.desc()])
    offset = (page - 1) * page_size
    query = query.order_by(*order_clauses).offset(offset).limit(page_size)
    jobs = (await db.execute(query)).scalars().all()

    items: List[JobResponse] = []
    for j in jobs:
        resp = JobResponse.model_validate(j)
        resp.source_name = j.source.name if j.source else "Public Source"
        if preference and MatchingService.has_meaningful_preferences(preference):
            score_res = MatchingService.calculate_match_score(j, preference)
            resp.match_score = score_res.total_score
            resp.match_reasons = [r.description for r in score_res.reasons]
        else:
            resp.match_score = None
            resp.match_reasons = []
        resp.is_saved = j.id in saved_ids
        resp.application_status = applications.get(j.id)
        items.append(resp)

    pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(
        items=items,
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
        .options(selectinload(Job.source))
        .join(SavedJob, SavedJob.job_id == Job.id)
        .where(SavedJob.user_id == current_user.id)
        .order_by(SavedJob.saved_at.desc())
    )
    jobs = (await db.execute(stmt)).scalars().all()

    pref_stmt = select(JobPreference).where(JobPreference.user_id == current_user.id)
    preference = (await db.execute(pref_stmt)).scalars().first()

    app_stmt = select(JobApplication).where(JobApplication.user_id == current_user.id)
    applications = {app.job_id: app.status.value for app in (await db.execute(app_stmt)).scalars().all()}

    items = []
    for j in jobs:
        resp = JobResponse.model_validate(j)
        resp.source_name = j.source.name if j.source else "Public Source"
        resp.is_saved = True
        resp.application_status = applications.get(j.id)
        if preference and MatchingService.has_meaningful_preferences(preference):
            score_res = MatchingService.calculate_match_score(j, preference)
            resp.match_score = score_res.total_score
            resp.match_reasons = [r.description for r in score_res.reasons]
        else:
            resp.match_score = None
            resp.match_reasons = []
        items.append(resp)
    return items


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_detail(
    job_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed view of a single job opportunity."""
    stmt = select(Job).options(selectinload(Job.source)).where(Job.id == job_id)
    job = (await db.execute(stmt)).scalars().first()
    if not job:
        raise NotFoundException(detail="Job not found")

    resp = JobResponse.model_validate(job)
    resp.source_name = job.source.name if job.source else "Public Source"

    if current_user:
        pref_stmt = select(JobPreference).where(JobPreference.user_id == current_user.id)
        preference = (await db.execute(pref_stmt)).scalars().first()
        if preference and MatchingService.has_meaningful_preferences(preference):
            score_res = MatchingService.calculate_match_score(job, preference)
            resp.match_score = score_res.total_score
            resp.match_reasons = [r.description for r in score_res.reasons]
        else:
            resp.match_score = None
            resp.match_reasons = []

        saved_stmt = select(SavedJob).where((SavedJob.user_id == current_user.id) & (SavedJob.job_id == job_id))
        resp.is_saved = (await db.execute(saved_stmt)).scalars().first() is not None

        app_stmt = select(JobApplication).where((JobApplication.user_id == current_user.id) & (JobApplication.job_id == job_id))
        app = (await db.execute(app_stmt)).scalars().first()
        resp.application_status = app.status.value if app else None

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


@router.post("/sync", summary="Trigger live real-time ingestion from active job sources (Admin)")
async def sync_live_jobs(
    admin: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger live real-time ingestion directly from active job sources.
    Requires administrator credentials. Reactivates returning jobs and marks stale jobs inactive.
    """
    from app.core.logging import logger
    from app.scrapers.sources.scraper_registry import get_scraper_class

    stmt = select(Source).where(Source.enabled == True)
    sources = (await db.execute(stmt)).scalars().all()
    if not sources:
        return {"status": "no_sources", "message": "No enabled sources configured", "new_jobs": 0, "total_jobs": 0}

    now = datetime.now(timezone.utc)
    existing_hashes = {h: id_ for h, id_ in (await db.execute(select(Job.dedupe_hash, Job.id))).all()}
    existing_keys = {(s_id, ext_id): id_ for s_id, ext_id, id_ in (await db.execute(select(Job.source_id, Job.external_id, Job.id))).all()}

    total_found = 0
    total_added = 0
    total_reactivated = 0
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
                existing_id = existing_hashes.get(j.dedupe_hash) or existing_keys.get((j.source_id, j.external_id))
                if existing_id:
                    # Update existing job last_seen_at and reactivate if inactive
                    existing_job = await db.get(Job, existing_id)
                    if existing_job:
                        existing_job.last_seen_at = now
                        if not existing_job.is_active:
                            existing_job.is_active = True
                            total_reactivated += 1
                    continue

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

            # Expire stale jobs: mark jobs inactive if not seen for 30 days for this source
            stale_cutoff = now - timedelta(days=30)
            stale_stmt = (
                select(Job)
                .where((Job.source_id == src.id) & (Job.is_active == True) & (Job.last_seen_at < stale_cutoff))
            )
            stale_jobs = (await db.execute(stale_stmt)).scalars().all()
            for sj in stale_jobs:
                sj.is_active = False

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
        "message": f"Synced {len(sources_synced)} sources. Found {total_found} live jobs, added {total_added} new unique jobs, reactivated {total_reactivated}.",
        "sources": sources_synced,
        "new_jobs": total_added,
        "total_active_jobs": total_active,
    }
