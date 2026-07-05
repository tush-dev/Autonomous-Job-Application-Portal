from app.workers.celery_app import celery_app


@celery_app.task
def refresh_job_cache():
    pass


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def crawl_job_source(self, source: str):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc)
