from celery import Celery

from constants.settings import settings

broker_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_BROKER_DB}"

celery_app = Celery("mercury", broker=broker_url, backend=broker_url, include=["worker.tasks"])
celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    broker_connection_retry_on_startup=True,
)
