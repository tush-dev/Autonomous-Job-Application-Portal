from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def parse_resume(self, resume_id: str, file_path: str):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_resume_ai(self, resume_id: str):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc)
