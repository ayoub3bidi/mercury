from uuid import uuid4
from unittest.mock import Mock

from models.Run import Run
from database.redis_db import redis_connect
from constants.settings import settings
from worker.tasks import execute_run


def test_completed_run_redelivery_does_not_reinvoke_agent(monkeypatch):
    run = Run(status="completed")
    db = Mock()
    db.get.return_value = run

    class Session:
        def __enter__(self):
            return db

        def __exit__(self, *_args):
            return False

    graph = Mock()
    monkeypatch.setattr("worker.tasks.SessionLocal", Session)
    monkeypatch.setattr("worker.tasks.agent_graph", graph)

    execute_run.run(str(uuid4()))

    graph.invoke.assert_not_called()


def test_worker_enables_late_acknowledgement_and_retries():
    assert execute_run.acks_late is True
    assert execute_run.max_retries == 3
    assert execute_run.autoretry_for == (Exception,)


def test_cache_and_broker_use_separate_redis_databases():
    assert redis_connect.connection_pool.connection_kwargs["db"] == settings.REDIS_CACHE_DB
    assert execute_run.app.conf.broker_url.endswith(f"/{settings.REDIS_BROKER_DB}")
    assert settings.REDIS_CACHE_DB != settings.REDIS_BROKER_DB
