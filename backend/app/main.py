import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func, select

from app.api.health import router as health_router
from app.api.v1.router import api_v1_router
from app.config import settings
from app.core.exceptions import BaseAppException
from app.core.logging import logger, setup_logging
from app.core.security import get_password_hash
from app.database import AsyncSessionLocal, Base, async_engine
from app.models.job import Job
from app.models.notification import NotificationConfig
from app.models.source import Source, SourceType
from app.models.user import JobPreference, User
from app.scrapers.sources.arbeitnow import ArbeitnowScraper
from app.scrapers.sources.remote_ok import RemoteOKScraper


async def seed_default_data():
    """Seed initial job sources and, in development only, demo accounts.

    Admin/demo account seeding is gated to ENVIRONMENT=development.
    Passwords are never hardcoded — they must be supplied via:
      SEED_ADMIN_PASSWORD and SEED_DEMO_PASSWORD environment variables.
    """
    async with AsyncSessionLocal() as session:
        # 1. Seed Real Job Sources (safe to run in all environments)
        src_stmt = select(Source)
        existing_sources = (await session.execute(src_stmt)).scalars().all()
        source_types = {s.scraper_type: s for s in existing_sources}

        if "remote_ok" not in source_types:
            remote_source = Source(
                name="RemoteOK (Live Remote Tech)",
                base_url="https://remoteok.com/api",
                source_type=SourceType.API,
                scraper_type="remote_ok",
                enabled=True,
                configuration={"items_key": None},
                rate_limit_delay=1.5,
            )
            session.add(remote_source)
            await session.flush()
            source_types["remote_ok"] = remote_source

        if "arbeitnow" not in source_types:
            arbeit_source = Source(
                name="Arbeitnow (Live Global Tech)",
                base_url="https://www.arbeitnow.com/api/job-board-api",
                source_type=SourceType.API,
                scraper_type="arbeitnow",
                enabled=True,
                configuration={},
                rate_limit_delay=1.5,
            )
            session.add(arbeit_source)
            await session.flush()
            source_types["arbeitnow"] = arbeit_source

        await session.commit()
        logger.info("Production job sources registered successfully")

        # 2. Demo account seeding — DEVELOPMENT ONLY
        if settings.ENVIRONMENT.lower() != "development":
            logger.info(
                "Skipping demo account seeding",
                environment=settings.ENVIRONMENT,
                reason="demo seeding is disabled outside development",
            )
        else:
            admin_password = os.environ.get("SEED_ADMIN_PASSWORD") or settings.SEED_ADMIN_PASSWORD
            demo_password = os.environ.get("SEED_DEMO_PASSWORD") or settings.SEED_DEMO_PASSWORD

            if not admin_password:
                logger.info(
                    "SEED_ADMIN_PASSWORD not set; skipping development admin account seeding. "
                    "Set SEED_ADMIN_PASSWORD in .env if local admin account is desired."
                )
            else:
                admin_stmt = select(User).where(User.email == "admin@jobintel.io")
                existing_admin = (await session.execute(admin_stmt)).scalars().first()
                if not existing_admin:
                    admin_user = User(
                        email="admin@jobintel.io",
                        hashed_password=get_password_hash(admin_password),
                        full_name="System Administrator",
                        is_superuser=True,
                        is_active=True,
                    )
                    session.add(admin_user)
                    await session.flush()

                    admin_pref = JobPreference(
                        user_id=admin_user.id,
                        keywords=["Python", "FastAPI", "Backend", "Full Stack", "DevOps"],
                        locations=["Remote", "Pakistan"],
                        employment_types=["Full-time", "Contract"],
                        work_modes=["Remote", "Hybrid"],
                        min_salary=60000,
                        max_salary=120000,
                    )
                    admin_notif = NotificationConfig(
                        user_id=admin_user.id,
                        email_notifications=True,
                        min_match_score=60,
                        # No default webhook URL — must be configured explicitly
                    )
                    session.add_all([admin_pref, admin_notif])
                    await session.commit()
                    logger.info("Development admin account seeded", email="admin@jobintel.io")

            if not demo_password:
                logger.info(
                    "SEED_DEMO_PASSWORD not set; skipping development candidate account seeding. "
                    "Set SEED_DEMO_PASSWORD in .env if local candidate account is desired."
                )
            else:
                demo_stmt = select(User).where(User.email == "candidate@jobintel.io")
                existing_demo = (await session.execute(demo_stmt)).scalars().first()
                if not existing_demo:
                    demo_user = User(
                        email="candidate@jobintel.io",
                        hashed_password=get_password_hash(demo_password),
                        full_name="Alex Engineer",
                        is_superuser=False,
                        is_active=True,
                    )
                    session.add(demo_user)
                    await session.flush()

                    cand_pref = JobPreference(
                        user_id=demo_user.id,
                        keywords=["Python", "FastAPI", "React", "Next.js"],
                        locations=["Remote", "Karachi"],
                        employment_types=["Full-time"],
                        work_modes=["Remote", "Hybrid"],
                        min_salary=50000,
                        max_salary=100000,
                    )
                    cand_notif = NotificationConfig(
                        user_id=demo_user.id,
                        email_notifications=True,
                        min_match_score=50,
                    )
                    session.add_all([cand_pref, cand_notif])
                    await session.commit()
                    logger.info("Development demo account seeded", email="candidate@jobintel.io")

        # 3. Ingest Initial Real Job Opportunities if table is empty or sparse
        jobs_count = (await session.execute(select(func.count(Job.id)))).scalar() or 0
        if jobs_count < 50:
            logger.info("Ingesting real-time live opportunities from production sources...")
            scrapers = []
            if "remote_ok" in source_types:
                scrapers.append(RemoteOKScraper(source_id=source_types["remote_ok"].id))
            if "arbeitnow" in source_types:
                scrapers.append(ArbeitnowScraper(source_id=source_types["arbeitnow"].id))

            existing_hashes = set((await session.execute(select(Job.dedupe_hash))).scalars().all())
            existing_keys = set((await session.execute(select(Job.source_id, Job.external_id))).all())
            now = datetime.now(timezone.utc)
            ingested_count = 0

            for scraper in scrapers:
                try:
                    jobs = await scraper.run()
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
                        session.add(job_record)
                        ingested_count += 1
                except Exception as e:
                    logger.error("Failed to ingest from scraper", scraper=scraper.__class__.__name__, error=str(e))

            await session.commit()
            logger.info("Real-time live opportunities ingested into feed", count=ingested_count)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info("Starting Job Intelligence Platform API", env=settings.ENVIRONMENT)

    # Auto-create tables for local execution (if Alembic migrations haven't run)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_default_data()
    yield
    # Shutdown
    logger.info("Shutting down API server")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade, automated Job Intelligence Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing & logging middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(process_time)
    return response


# Centralized exception handlers
@app.exception_handler(BaseAppException)
async def custom_app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled server exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "code": "INTERNAL_SERVER_ERROR"},
    )


# Include Routers
app.include_router(health_router)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
