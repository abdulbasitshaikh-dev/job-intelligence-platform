import asyncio
from sqlalchemy import select
from app.celery_app import celery_app
from app.core.logging import logger
from app.database import SyncSessionLocal
from app.models.job import Job
from app.models.user import User, JobPreference
from app.models.notification import NotificationConfig
from app.services.matching import MatchingService
from app.services.notification import NotificationService


async def _async_match_and_notify() -> dict:
    with SyncSessionLocal() as session:
        # Get active jobs
        jobs = session.execute(select(Job).where(Job.is_active == True).limit(100)).scalars().all()
        # Get users with configured preferences & notifications
        users = session.execute(select(User).where(User.is_active == True)).scalars().all()

        notifications_sent = 0
        for user in users:
            pref = session.execute(select(JobPreference).where(JobPreference.user_id == user.id)).scalars().first()
            config = session.execute(select(NotificationConfig).where(NotificationConfig.user_id == user.id)).scalars().first()
            
            if not pref:
                continue

            # Fallback notification config if not explicitly set
            if not config:
                config = NotificationConfig(user_id=user.id, email_notifications=True, min_match_score=60)

            for job in jobs:
                score_res = MatchingService.calculate_match_score(job, pref)
                if score_res.total_score >= config.min_match_score:
                    await NotificationService.process_job_match_notification(
                        config=config,
                        user=user,
                        job=job,
                        match_score=score_res.total_score,
                    )
                    notifications_sent += 1

        return {"status": "SUCCESS", "notifications_sent": notifications_sent}


@celery_app.task(name="app.tasks.matching.match_and_notify_task")
def match_and_notify_task():
    """Periodic Celery task to evaluate job matches and dispatch notifications."""
    return asyncio.run(_async_match_and_notify())
