from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx

from app.config import settings
from app.core.logging import logger
from app.models.job import Job
from app.models.notification import NotificationConfig
from app.models.user import User


class NotificationService:
    """Service to handle notification deliveries via Webhooks (n8n compatible) and Email."""

    @staticmethod
    async def send_webhook(
        webhook_url: str,
        event_name: str,
        job: Job,
        user: User,
        match_score: int,
        secret: Optional[str] = None,
    ) -> bool:
        """Deliver standard JSON webhook payload (compatible with n8n, Slack, generic automation)."""
        payload: Dict[str, Any] = {
            "event": event_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "match_score": match_score,
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "work_mode": job.work_mode.value,
                "employment_type": job.employment_type.value,
                "url": job.canonical_url or job.url,
                "posted_at": job.posted_at.isoformat() if job.posted_at else None,
            },
            "user": {
                "id": user.id,
                "email": user.email,
            },
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "JobIntelligencePlatform-Webhook/1.0",
        }
        if secret:
            headers["X-Webhook-Secret"] = secret

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(webhook_url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info("Webhook delivered successfully", webhook_url=webhook_url, event=event_name, job_id=job.id)
                return True
        except Exception as e:
            logger.error("Failed to deliver webhook", webhook_url=webhook_url, error=str(e))
            return False

    @staticmethod
    async def send_email_notification(user_email: str, job: Job, match_score: int) -> bool:
        """Simulate/send HTML job notification email."""
        logger.info(
            "Simulating Email notification sent",
            to_email=user_email,
            job_title=job.title,
            company=job.company,
            match_score=match_score,
        )
        return True

    @classmethod
    async def process_job_match_notification(
        cls,
        config: NotificationConfig,
        user: User,
        job: Job,
        match_score: int,
    ) -> None:
        """Evaluate user notification thresholds and trigger configured channels."""
        if match_score < config.min_match_score:
            return

        if config.webhook_url:
            await cls.send_webhook(
                webhook_url=config.webhook_url,
                event_name="job.match",
                job=job,
                user=user,
                match_score=match_score,
                secret=config.webhook_secret,
            )

        if config.email_notifications:
            await cls.send_email_notification(
                user_email=user.email,
                job=job,
                match_score=match_score,
            )
