from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery = Celery(
    "fantasy_arena",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)
celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "settle-completed-matches": {
            "task": "app.workers.tasks.settle_completed_matches",
            "schedule": crontab(minute="*/2"),
        },
        "reconcile-ledger": {
            "task": "app.workers.tasks.reconcile_ledger",
            "schedule": crontab(minute=0, hour="*/6"),
        },
        "expire-self-exclusions": {
            "task": "app.workers.tasks.expire_self_exclusions",
            "schedule": crontab(minute=10),
        },
    },
)
