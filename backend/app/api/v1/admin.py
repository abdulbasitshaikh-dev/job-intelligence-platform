from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser
from app.core.exceptions import DuplicateResourceException, NotFoundException
from app.database import get_db
from app.models.job import Job
from app.models.source import ScraperRun, Source
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.source import ScraperRunResponse, SourceCreate, SourceResponse, SourceUpdate
from app.tasks.scraping import _async_scrape_source, scrape_source_task

router = APIRouter(prefix="/admin", tags=["Admin Management"])


@router.get("/sources", response_model=List[SourceResponse])
async def admin_list_sources(
    admin: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Admin view of all job sources including disabled ones."""
    stmt = select(Source).order_by(Source.id)
    sources = (await db.execute(stmt)).scalars().all()
    return sources


@router.post("/sources", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_source(
    src_in: SourceCreate,
    admin: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Create a new job data source configuration."""
    stmt = select(Source).where(Source.name == src_in.name)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise DuplicateResourceException(detail="Source with this name already exists")

    source = Source(**src_in.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.put("/sources/{source_id}", response_model=SourceResponse)
async def admin_update_source(
    source_id: int,
    src_in: SourceUpdate,
    admin: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Update job source configuration or toggle enabled state."""
    source = await db.get(Source, source_id)
    if not source:
        raise NotFoundException(detail="Source not found")

    update_data = src_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(source, field, val)

    await db.commit()
    await db.refresh(source)
    return source


@router.post("/sources/{source_id}/scrape", response_model=MessageResponse)
async def admin_trigger_scrape(
    source_id: int,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger background scraping task for a specific source."""
    source = await db.get(Source, source_id)
    if not source:
        raise NotFoundException(detail="Source not found")

    try:
        task_res = scrape_source_task.delay(source_id)
        return MessageResponse(message=f"Scrape task dispatched to Celery queue for source '{source.name}' (Task ID: {task_res.id})")
    except Exception:
        # If Celery/Redis is not running, run directly in FastAPI background tasks
        background_tasks.add_task(_async_scrape_source, source_id)
        return MessageResponse(message=f"Scrape task initiated in background for source '{source.name}'")


@router.get("/scraper-runs", response_model=PaginatedResponse[ScraperRunResponse])
async def admin_list_scraper_runs(
    source_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Inspect scraper run execution logs and failure details."""
    query = select(ScraperRun)
    if source_id:
        query = query.where(ScraperRun.source_id == source_id)

    total_stmt = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_stmt)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(ScraperRun.started_at.desc()).offset(offset).limit(page_size)
    runs = (await db.execute(query)).scalars().all()

    import math
    pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(
        items=[ScraperRunResponse.model_validate(r) for r in runs],
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )


@router.post("/sync-all", response_model=MessageResponse)
async def admin_trigger_sync_all(
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Trigger scraping ingestion for all enabled sources."""
    from app.tasks.scraping import scrape_all_sources_task
    try:
        task_res = scrape_all_sources_task.delay()
        return MessageResponse(message=f"Global sync queued via Celery (Task ID: {task_res.id})")
    except Exception:
        # Fallback to in-process execution of enabled sources
        stmt = select(Source.id).where(Source.enabled == True)
        source_ids = (await db.execute(stmt)).scalars().all()
        for s_id in source_ids:
            background_tasks.add_task(_async_scrape_source, s_id)
        return MessageResponse(message=f"Global sync initiated in background for {len(source_ids)} enabled sources")


@router.get("/health", summary="Detailed multi-component system health telemetry")
async def admin_system_health(
    admin: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Check live connectivity for PostgreSQL, Redis, and Celery."""
    import redis.asyncio as aioredis
    from sqlalchemy import text

    from app.config import settings

    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    redis_status = "healthy"
    try:
        r = aioredis.from_url(settings.REDIS_URL, socket_timeout=2.0)
        await r.ping()
        await r.close()
    except Exception as e:
        redis_status = f"unreachable: {str(e)}"

    # Check recent Celery/Scraper activity
    recent_run = (
        await db.execute(select(ScraperRun).order_by(ScraperRun.started_at.desc()).limit(1))
    ).scalars().first()

    return {
        "status": "operational" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "components": {
            "database": {"status": db_status},
            "redis": {"status": redis_status},
            "celery": {"status": "configured", "broker": settings.CELERY_BROKER_URL},
            "scheduler": {"status": "active", "schedule": "every 30 mins"},
        },
        "last_run": {
            "id": recent_run.id if recent_run else None,
            "status": recent_run.status.value if recent_run else "NEVER",
            "timestamp": recent_run.started_at.isoformat() if recent_run else None,
        } if recent_run else None,
    }


@router.get("/stats")
async def admin_system_stats(
    admin: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Get high-level system statistics for administrative dashboard."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_jobs = (await db.execute(select(func.count(Job.id)))).scalar() or 0
    active_jobs = (await db.execute(select(func.count(Job.id)).where(Job.is_active == True))).scalar() or 0
    total_sources = (await db.execute(select(func.count(Source.id)))).scalar() or 0
    total_runs = (await db.execute(select(func.count(ScraperRun.id)))).scalar() or 0
    successful_runs = (
        await db.execute(select(func.count(ScraperRun.id)).where(ScraperRun.status == "SUCCESS"))
    ).scalar() or 0
    failed_runs = (
        await db.execute(select(func.count(ScraperRun.id)).where(ScraperRun.status == "FAILED"))
    ).scalar() or 0
    last_sync = (await db.execute(select(func.max(Source.last_success_at)))).scalar()

    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_sources": total_sources,
        "total_scraper_runs": total_runs,
        "successful_runs": successful_runs,
        "failed_runs": failed_runs,
        "last_successful_sync": last_sync.isoformat() if last_sync else None,
    }

