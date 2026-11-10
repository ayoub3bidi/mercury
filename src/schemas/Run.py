from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RunCreate(BaseModel):
    prompt: str
    token_budget: int | None = None


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    result: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime
