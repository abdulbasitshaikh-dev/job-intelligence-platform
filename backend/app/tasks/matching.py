import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.celery_app import celery_app
from app.database import SyncSessionLocal
from app.models.job import Job
from app.models.notification import NotificationConfig, NotificationLog
from app.models.user import JobPreference, User
from app.services.matching import MatchingService
from app.services.notification import NotificationService


async def _async_match_and_notify() -> dict:
    with SyncSessionLocal() as session:
        # Get active jobs
        jobs = session.execute(select(Job).where(Job.is_active == True).limit(100)).scalars().all()
        # Get active users
        users = session.execute(select(User).where(User.is_active == True)).scalars().all()

        notifications_sent = 0
        now = datetime.now(timezone.utc)

        for user in users:
            pref = session.execute(select(JobPreference).where(JobPreference.user_id == user.id)).scalars().first()
            config = session.execute(select(NotificationConfig).where(NotificationConfig.user_id == user.id)).scalars().first()

            if not pref:
                continue

            if not config:
                config = NotificationConfig(user_id=user.id, email_notifications=True, min_match_score=60)

            # Retrieve existing notification logs for this user
            sent_keys = {
                (log.job_id, log.channel)
                for log in session.execute(
                    select(NotificationLog).where(NotificationLog.user_id == user.id)
                ).scalars().all()
            }

            for job in jobs:
                score_res = MatchingService.calculate_match_score(job, pref)
                if score_res.total_score >= config.min_match_score:
                    # Only dispatch if not already alerted on that channel
                    channels_to_alert = []
                    if config.webhook_url and (job.id, "webhook") not in sent_keys:
                        channels_to_alert.append("webhook")
                    if config.email_notifications and (job.id, "email") not in sent_keys:
                        channels_to_alert.append("email")

                    if not channels_to_alert:
                        continue

                    deliveries = await NotificationService.process_job_match_notification(
                        config=config,
                        user=user,
                        job=job,
                        match_score=score_res.total_score,
                    )

                    for channel, success in deliveries.items():
                        if success and channel in channels_to_alert:
                            log = NotificationLog(
                                user_id=user.id,
                                job_id=job.id,
                                channel=channel,
                                sent_at=now,
                                match_score=score_res.total_score,
                            )
                            session.add(log)
                            sent_keys.add((job.id, channel))
                            notifications_sent += 1

        session.commit()
        return {"status": "SUCCESS", "notifications_sent": notifications_sent}


@celery_app.task(name="app.tasks.matching.match_and_notify_task")
def match_and_notify_task():
    """Periodic Celery task to evaluate job matches and dispatch notifications."""
    return asyncio.run(_async_match_and_notify())

