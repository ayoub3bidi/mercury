from fastapi import Response

import routes.health as health


def test_readiness_reports_redis_failure(monkeypatch):
    class Database:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, _query):
            return None

    class Redis:
        @staticmethod
        def ping():
            raise ConnectionError("redis is down")

    monkeypatch.setattr(health, "SessionLocal", Database)
    monkeypatch.setattr(health, "redis_connect", Redis())
    response = Response()

    result = health.get_readiness(response)

    assert response.status_code == 503
    assert result == {
        "status": "not_ready",
        "ready": False,
        "checks": {"postgres": True, "redis": False},
    }


def test_readiness_reports_postgres_failure(monkeypatch):
    class Database:
        def __enter__(self):
            raise ConnectionError("postgres is down")

        def __exit__(self, *_args):
            return False

    class Redis:
        @staticmethod
        def ping():
            return True

    monkeypatch.setattr(health, "SessionLocal", Database)
    monkeypatch.setattr(health, "redis_connect", Redis())
    response = Response()

    result = health.get_readiness(response)

    assert response.status_code == 503
    assert result["checks"] == {"postgres": False, "redis": True}
