import asyncio
from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "job_intelligence_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_max_tasks_per_child=50,
)

# Celery Beat Scheduled Tasks
celery_app.conf.beat_schedule = {
    "scrape-all-enabled-sources-every-30-mins": {
        "task": "app.tasks.scraping.scrape_all_sources_task",
        "schedule": crontab(minute="*/30"),
    },
    "evaluate-matches-and-notify-every-1-hour": {
        "task": "app.tasks.matching.match_and_notify_task",
        "schedule": crontab(minute="0", hour="*"),
    },
}
