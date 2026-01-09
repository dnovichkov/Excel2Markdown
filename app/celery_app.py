"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "excel2markdown",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.conversion_tasks",
        "app.tasks.cleanup_tasks",
    ],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=86400,  # Results expire after 24 hours
    beat_schedule={
        "cleanup-old-files": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_files",
            "schedule": crontab(hour=3, minute=0),  # Daily at 3:00 UTC
        },
    },
)
