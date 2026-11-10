from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import update

from agent.graph import agent_graph
from constants.settings import settings
from database.postgres_db import SessionLocal
from models.Run import Run
from worker.celery_app import celery_app


@celery_app.task(
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
    time_limit=settings.CELERY_TASK_TIME_LIMIT,
)
def execute_run(self, run_id: str) -> None:
    with SessionLocal() as db:
        run = db.get(Run, UUID(run_id))
        if run is None or run.status == "completed":
            return
        run.status = "running"
        run.error = None
        db.commit()
        prompt, token_budget = run.prompt, run.token_budget

    try:
        result = agent_graph.invoke({"prompt": prompt, "token_budget": token_budget, "result": ""})["result"]
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            with SessionLocal() as db:
                db.execute(
                    update(Run)
                    .where(Run.id == UUID(run_id))
                    .values(status="failed", error=str(exc)[:2000], updated_at=datetime.now(timezone.utc))
                )
                db.commit()
        raise

    with SessionLocal() as db:
        db.execute(
            update(Run)
            .where(Run.id == UUID(run_id), Run.status != "completed")
            .values(status="completed", result=result, updated_at=datetime.now(timezone.utc))
        )
        db.commit()
