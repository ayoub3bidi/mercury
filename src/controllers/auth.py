"""Auth controller: token (OAuth2 password) login."""

from datetime import timedelta

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from constants.settings import settings
from utils.security import authenticate_by_username_or_email, create_access_token


def login_for_access_token(form_data: OAuth2PasswordRequestForm, db: Session):
    """Validate username/email + password and return a JWT token."""
    user = authenticate_by_username_or_email(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
