"""
Seed Demo Data Script for Job Intelligence Platform
Populates sample users, job opportunities, applications, and preference records.
"""
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from app.database import AsyncSessionLocal, async_engine, Base
from app.core.security import get_password_hash
from app.models.user import User, JobPreference
from app.models.source import Source, SourceType
from app.models.job import Job, EmploymentType, WorkMode
from app.models.application import JobApplication, ApplicationStatus
from app.models.saved_job import SavedJob
from app.models.notification import NotificationConfig
from app.services.normalization import NormalizationService


EXTRA_DEMO_JOBS = [
    {
        "external_id": "seed-001",
        "title": "Lead Platform Engineer (FastAPI & Kubernetes)",
        "company": "ScalePulse AI",
        "location": "Remote (Worldwide)",
        "description": "Architect high-throughput microservices using FastAPI, Redis, and Celery. Manage Kubernetes deployments and data ingestion pipelines.",
        "url": "https://example.com/jobs/lead-platform-engineer",
        "work_mode": WorkMode.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "salary_min": 110000,
        "salary_max": 145000,
    },
    {
        "external_id": "seed-002",
        "title": "Senior React & TypeScript Frontend Architect",
        "company": "Veloce Systems",
        "location": "Remote (USA / EMEA)",
        "description": "Design modern, glassmorphic real-time analytics dashboards using React 18, TypeScript, Tailwind CSS, and Vite.",
        "url": "https://example.com/jobs/senior-frontend-architect",
        "work_mode": WorkMode.REMOTE,
        "employment_type": EmploymentType.FULL_TIME,
        "salary_min": 95000,
        "salary_max": 130000,
    },
    {
        "external_id": "seed-003",
        "title": "Data Engineering & Web Scraping Specialist",
        "company": "DataWeave Global",
        "location": "Karachi, Pakistan (Hybrid)",
        "description": "Build high-resilience web scrapers using BeautifulSoup, Playwright, and httpx. Handle canonical deduplication and ETL normalization into PostgreSQL.",
        "url": "https://example.com/jobs/data-engineering-scraper",
        "work_mode": WorkMode.HYBRID,
        "employment_type": EmploymentType.FULL_TIME,
        "salary_min": 65000,
        "salary_max": 90000,
    },
    {
        "external_id": "seed-004",
        "title": "Junior Backend Developer (Python & PostgreSQL)",
        "company": "NexStep Interactive",
        "location": "Lahore, Pakistan",
        "description": "Entry-level to mid backend position working on RESTful APIs with FastAPI, SQLAlchemy 2.0, and automated pytest suites.",
        "url": "https://example.com/jobs/junior-backend-dev",
        "work_mode": WorkMode.ON_SITE,
        "employment_type": EmploymentType.FULL_TIME,
        "salary_min": 35000,
        "salary_max": 50000,
    },
    {
        "external_id": "seed-005",
        "title": "DevOps / Site Reliability Engineer (Celery & Redis)",
        "company": "CloudHaven Ops",
        "location": "Remote",
        "description": "Ensure 99.99% uptime for Celery Beat scheduled tasks, Redis message brokers, PostgreSQL replicas, and Docker container clusters.",
        "url": "https://example.com/jobs/devops-sre-redis",
        "work_mode": WorkMode.REMOTE,
        "employment_type": EmploymentType.CONTRACT,
        "salary_min": 80000,
        "salary_max": 115000,
    },
]


async def seed():
    print("Connecting to database and initializing schemas...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Ensure Demo Source exists
        source_stmt = select(Source).where(Source.scraper_type == "demo_fixture")
        source = (await session.execute(source_stmt)).scalars().first()
        if not source:
            source = Source(
                name="Demo Jobs Fixture",
                base_url="http://localhost:8000/demo-jobs",
                source_type=SourceType.API,
                scraper_type="demo_fixture",
                enabled=True,
                configuration={},
                rate_limit_delay=1.0,
            )
            session.add(source)
            await session.commit()
            await session.refresh(source)
            print("Created default Demo Source.")

        # 2. Seed Admin User
        admin = (await session.execute(select(User).where(User.email == "admin@jobintel.io"))).scalars().first()
        if not admin:
            admin = User(
                email="admin@jobintel.io",
                hashed_password=get_password_hash("Admin12345!"),
                full_name="System Administrator",
                is_superuser=True,
                is_active=True,
            )
            session.add(admin)
            await session.flush()
            pref = JobPreference(
                user_id=admin.id,
                keywords=["Python", "FastAPI", "React", "DevOps"],
                locations=["Remote", "Pakistan"],
                employment_types=["Full-time", "Contract"],
                work_modes=["Remote", "Hybrid"],
                min_salary=60000,
                max_salary=140000,
            )
            session.add(pref)
            notif = NotificationConfig(
                user_id=admin.id,
                email_notifications=True,
                min_match_score=60,
                webhook_url="http://localhost:8000/api/v1/webhooks/job-events",
            )
            session.add(notif)
            await session.commit()
            print("Seeded Admin User: admin@jobintel.io / Admin12345!")

        # 3. Seed Candidate Demo User
        cand = (await session.execute(select(User).where(User.email == "candidate@jobintel.io"))).scalars().first()
        if not cand:
            cand = User(
                email="candidate@jobintel.io",
                hashed_password=get_password_hash("Candidate123!"),
                full_name="Alex Engineer",
                is_superuser=False,
                is_active=True,
            )
            session.add(cand)
            await session.flush()
            cand_pref = JobPreference(
                user_id=cand.id,
                keywords=["Python", "FastAPI", "Backend", "React"],
                locations=["Remote", "Karachi"],
                employment_types=["Full-time"],
                work_modes=["Remote", "Hybrid"],
                min_salary=50000,
                max_salary=110000,
            )
            session.add(cand_pref)
            await session.commit()
            print("Seeded Candidate User: candidate@jobintel.io / Candidate123!")

        # 4. Seed Extra Jobs
        now = datetime.now(timezone.utc)
        created_jobs = []
        for job_data in EXTRA_DEMO_JOBS:
            dedupe_hash = NormalizationService.compute_dedupe_hash(
                source.id, job_data["title"], job_data["company"], job_data["location"]
            )
            existing = (await session.execute(select(Job).where(Job.dedupe_hash == dedupe_hash))).scalars().first()
            if not existing:
                j = Job(
                    source_id=source.id,
                    external_id=job_data["external_id"],
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    description=job_data["description"],
                    url=job_data["url"],
                    canonical_url=NormalizationService.normalize_url(job_data["url"]),
                    employment_type=job_data["employment_type"],
                    work_mode=job_data["work_mode"],
                    salary_min=job_data["salary_min"],
                    salary_max=job_data["salary_max"],
                    currency="USD",
                    posted_at=now,
                    first_seen_at=now,
                    last_seen_at=now,
                    is_active=True,
                    dedupe_hash=dedupe_hash,
                    raw_data={"source": "seed_demo_data"},
                )
                session.add(j)
                created_jobs.append(j)

        await session.commit()
        print(f"Seeded {len(created_jobs)} extra job opportunities.")

        # 5. Seed Saved Jobs & Applications for Candidate
        if created_jobs and cand:
            # Save first job
            save_stmt = select(SavedJob).where(SavedJob.user_id == cand.id, SavedJob.job_id == created_jobs[0].id)
            if not (await session.execute(save_stmt)).scalars().first():
                session.add(SavedJob(user_id=cand.id, job_id=created_jobs[0].id))

            # Add application tracking
            app_stmt = select(JobApplication).where(JobApplication.user_id == cand.id, JobApplication.job_id == created_jobs[0].id)
            if not (await session.execute(app_stmt)).scalars().first():
                session.add(
                    JobApplication(
                        user_id=cand.id,
                        job_id=created_jobs[0].id,
                        status=ApplicationStatus.INTERVIEW,
                        notes="Screening interview scheduled for next Tuesday at 2 PM UTC. Review architecture questions.",
                        applied_at=now,
                    )
                )

            if len(created_jobs) > 1:
                app2_stmt = select(JobApplication).where(JobApplication.user_id == cand.id, JobApplication.job_id == created_jobs[1].id)
                if not (await session.execute(app2_stmt)).scalars().first():
                    session.add(
                        JobApplication(
                            user_id=cand.id,
                            job_id=created_jobs[1].id,
                            status=ApplicationStatus.APPLIED,
                            notes="Applied via company portal. Tailored resume highlighting TypeScript & Vite experience.",
                            applied_at=now,
                        )
                    )

            await session.commit()
            print("Seeded sample saved jobs and tracked applications.")

    print("\n[SUCCESS] Demo data seeded successfully! You can now log in with:")
    print("  Administrator: admin@jobintel.io / Admin12345!")
    print("  Candidate:     candidate@jobintel.io / Candidate123!")


if __name__ == "__main__":
    asyncio.run(seed())
