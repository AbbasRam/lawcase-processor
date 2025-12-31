from celery import Celery
from pdf_processor.config import settings

celery_app = Celery(
    "pdf_processor",
    broker=settings.REDIS_BROKER_URL,
    backend=settings.REDIS_BACKEND_URL,
    include=["pdf_processor.tasks"]
)

celery_app.conf.update(
    task_track_started=True,
)
