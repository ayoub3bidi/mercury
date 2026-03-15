"""Auth routes: OAuth2 token endpoint."""
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from controllers.auth import login_for_access_token
from database.postgres_db import get_db
from schemas.Token import Token

router = APIRouter(tags=["Access Token"])


@router.post("/token", response_model=Token)
def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """OAuth2 compatible token login: submit username and password to get a JWT."""
    return login_for_access_token(form_data, db)
