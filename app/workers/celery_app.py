from celery import Celery

from app.config import REDIS_URL

celery = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)
celery.conf.imports = ("app.workers.tasks",)