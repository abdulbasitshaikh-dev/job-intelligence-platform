from typing import Any, Dict
from fastapi import APIRouter, Header, Request, status
from app.core.logging import logger

router = APIRouter(prefix="/webhooks", tags=["Webhooks & n8n"])


@router.post("/job-events", status_code=status.HTTP_200_OK)
async def receive_job_webhook(
    payload: Dict[str, Any],
    request: Request,
    x_webhook_secret: str = Header(None),
):
    """
    Sample Webhook Receiver Endpoint (n8n / external webhook integration target).
    Receives events like `job.match` and logs payload details.
    """
    event = payload.get("event", "unknown")
    job_data = payload.get("job", {})
    user_data = payload.get("user", {})
    score = payload.get("match_score", 0)

    logger.info(
        "Received job webhook event",
        event=event,
        job_id=job_data.get("id"),
        job_title=job_data.get("title"),
        user_id=user_data.get("id"),
        score=score,
    )

    return {
        "status": "received",
        "event": event,
        "job_id": job_data.get("id"),
        "processed": True,
    }
