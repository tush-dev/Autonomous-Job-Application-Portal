from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_ai_request(self, request_id: str, agent_type: str, payload: dict):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc)
