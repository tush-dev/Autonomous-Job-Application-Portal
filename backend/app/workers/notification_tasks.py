from app.workers.celery_app import celery_app


@celery_app.task
def send_interview_reminders():
    pass


@celery_app.task
def send_email_notification(to: str, subject: str, body: str):
    pass
