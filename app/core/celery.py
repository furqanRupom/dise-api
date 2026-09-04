from celery import Celery

from app.core.config import settings

raw_url = getattr(settings, "REDIS_URL", None)
if not raw_url or str(raw_url).strip().lower() in ("none", "null", ""):
    redis_url = "redis://localhost:6379/0"
else:
    redis_url = str(raw_url)

celery_app = Celery(
    "app_worker",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Ensures tasks are acknowledged ONLY after execution completes
    task_acks_late=True,
    # Re-queue tasks if worker crashes mid-execution
    task_reject_on_worker_lost=True,
)

celery_app.autodiscover_tasks(["app.tasks"])
