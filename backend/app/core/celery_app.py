import os
from celery import Celery

# Read broker and backend URLs from environment or fall back to local Redis defaults
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", BROKER_URL)

celery_app = Celery(
    "music_sync_hub",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=[],  # task modules will be added later
)

# Basic configuration (can be extended later)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # 1 hour
)

@celery_app.task(name="health.check")
def health_check() -> str:  # simple task so Flower UI isn't empty
    """Return 'ok' to confirm the worker is responsive."""
    return "ok" 