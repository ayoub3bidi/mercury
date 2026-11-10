from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from constants.settings import settings
from routes.runs import create_run
from schemas.Run import RunCreate


class Query:
    def filter(self, _expression):
        return self

    def first(self):
        return None


class Database:
    def __init__(self):
        self.added = None

    def query(self, _model):
        return Query()

    def add(self, run):
        self.added = run

    def commit(self):
        self.added.id = uuid4()
        self.added.created_at = datetime.now(timezone.utc)
        self.added.updated_at = self.added.created_at

    def refresh(self, _run):
        return None


@pytest.mark.parametrize("token_budget", [0, settings.RUN_TOKEN_BUDGET + 1])
def test_invalid_token_budget_is_rejected(token_budget):
    with pytest.raises(HTTPException) as error:
        create_run(RunCreate(prompt="prompt", token_budget=token_budget), Database(), None)

    assert error.value.status_code == 400


def test_omitted_token_budget_uses_configured_default(monkeypatch):
    db = Database()
    queue = Mock()
    monkeypatch.setattr("routes.runs.execute_run.delay", queue)

    run = create_run(RunCreate(prompt="prompt"), db, "request-1")

    assert run.token_budget == settings.RUN_TOKEN_BUDGET
    queue.assert_called_once_with(str(run.id))
