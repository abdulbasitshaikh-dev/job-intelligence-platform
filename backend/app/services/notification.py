import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from app.core.logging import logger
from app.core.security import is_safe_webhook_url
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
        """Deliver standard JSON webhook payload with SSRF validation and HMAC signing."""
        if not is_safe_webhook_url(webhook_url):
            logger.warning("Blocked potential SSRF webhook delivery", url=webhook_url)
            return False

        payload: Dict[str, Any] = {
            "event": event_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "match_score": match_score,
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "work_mode": job.work_mode.value if hasattr(job.work_mode, "value") else str(job.work_mode),
                "employment_type": job.employment_type.value if hasattr(job.employment_type, "value") else str(job.employment_type),
                "url": job.canonical_url or job.url,
                "salary_min": float(job.salary_min) if job.salary_min is not None else None,
                "salary_max": float(job.salary_max) if job.salary_max is not None else None,
                "currency": job.currency,
                "posted_at": job.posted_at.isoformat() if job.posted_at else None,
            },
            "user": {
                "id": user.id,
                "email": user.email,
            },
        }

        raw_body = json.dumps(payload, sort_keys=True)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "JobIntelligencePlatform-Webhook/1.0",
        }
        if secret:
            signature = hmac.new(secret.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha256).hexdigest()
            headers["X-Webhook-Secret"] = secret
            headers["X-JobIntel-Signature"] = f"sha256={signature}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(webhook_url, content=raw_body, headers=headers)
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
    ) -> Dict[str, bool]:
        """Evaluate user notification thresholds and trigger configured channels."""
        results = {"webhook": False, "email": False}
        if match_score < config.min_match_score:
            return results

        if config.webhook_url:
            delivered = await cls.send_webhook(
                webhook_url=config.webhook_url,
                event_name="job.match",
                job=job,
                user=user,
                match_score=match_score,
                secret=config.webhook_secret,
            )
            results["webhook"] = delivered

        if config.email_notifications:
            sent = await cls.send_email_notification(
                user_email=user.email,
                job=job,
                match_score=match_score,
            )
            results["email"] = sent

        return results

