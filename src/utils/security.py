import re
from datetime import datetime, timedelta
from typing import Union

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from constants.settings import settings
from constants.regex import email_regex, password_regex
from models.User import User

crypting_algorithm = "sha256_crypt" if settings.JWT_ALGORITHM == "HS256" else "bcrypt"

pwd_context = CryptContext(schemes=[crypting_algorithm], deprecated="auto")

# Pre-hashed password used when the user does not exist (timing-attack mitigation).
DUMMY_HASH = pwd_context.hash("__mercury_timing_dummy__")


def validate_email(email):
    if re.search(email_regex, email):
        return True
    return False


def validate_password(password):
    if re.search(password_regex, password):
        return True
    return False


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def _authenticate_user_record(user: User | None, password: str) -> User | None:
    if user is None or user.password is None:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.password):
        return None
    return user


def authenticate_by_email(email: str, password: str, db) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    return _authenticate_user_record(user, password)


def authenticate_by_username_or_email(username_or_email: str, password: str, db) -> User | None:
    if "@" in username_or_email:
        return authenticate_by_email(username_or_email, password, db)
    user = db.query(User).filter(User.username == username_or_email).first()
    return _authenticate_user_record(user, password)


def authenticate_user(payload, db):
    user = authenticate_by_email(payload.email, payload.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
