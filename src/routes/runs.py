from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from constants.settings import settings
from database.postgres_db import get_db
from models.Run import Run
from schemas.Run import RunCreate, RunResponse
from worker.tasks import execute_run

router = APIRouter()


@router.post("/runs", status_code=status.HTTP_202_ACCEPTED, response_model=RunResponse)
def create_run(
    payload: RunCreate,
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt must not be empty")
    budget = payload.token_budget if payload.token_budget is not None else settings.RUN_TOKEN_BUDGET
    if budget <= 0 or budget > settings.RUN_TOKEN_BUDGET:
        raise HTTPException(status_code=400, detail=f"token_budget must be between 1 and {settings.RUN_TOKEN_BUDGET}")

    key = idempotency_key or str(uuid4())
    run = db.query(Run).filter(Run.idempotency_key == key).first()
    if run is None:
        run = Run(idempotency_key=key, prompt=prompt, token_budget=budget)
        db.add(run)
        try:
            db.commit()
            db.refresh(run)
            execute_run.delay(str(run.id))
        except IntegrityError:
            db.rollback()
            run = db.query(Run).filter(Run.idempotency_key == key).first()
            if run is None:
                raise
    elif run.prompt != prompt:
        raise HTTPException(status_code=409, detail="Idempotency-Key was already used with a different prompt")
    return run


@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    try:
        parsed_id = UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found") from None
    run = db.get(Run, parsed_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
