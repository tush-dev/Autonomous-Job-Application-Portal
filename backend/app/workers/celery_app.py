from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "jobagent",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    include=[
        "app.workers.resume_tasks",
        "app.workers.job_search_tasks",
        "app.workers.ai_tasks",
        "app.workers.notification_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_max_tasks_per_child=200,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "refresh-job-cache": {
            "task": "app.workers.job_search_tasks.refresh_job_cache",
            "schedule": 1800.0,
        },
        "send-interview-reminders": {
            "task": "app.workers.notification_tasks.send_interview_reminders",
            "schedule": 300.0,
        },
    },
)
