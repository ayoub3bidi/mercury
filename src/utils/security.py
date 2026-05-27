import re
from datetime import datetime, timedelta
from typing import Union

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from constants.settings import settings
from constants.regex import email_regex, password_regex
from models.User import User
from repositories.user import UserRepository

password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))

# Legacy passlib hashes (sha256_crypt from seeded admin / HS256-era installs).
_legacy_pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# Pre-hashed password used when the user does not exist (timing-attack mitigation).
DUMMY_HASH = password_hash.hash("__mercury_timing_dummy__")


def validate_email(email):
    if re.search(email_regex, email):
        return True
    return False


def validate_password(password):
    if re.search(password_regex, password):
        return True
    return False


def _verify_legacy_sha256(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password.startswith("$5$"):
        return False
    return _legacy_pwd_context.verify(plain_password, hashed_password)


def verify_password(plain_password: str, hashed_password: str) -> tuple[bool, str | None]:
    if hashed_password is None:
        return False, None
    if _verify_legacy_sha256(plain_password, hashed_password):
        return True, password_hash.hash(plain_password)
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def _persist_password_upgrade(db, user: User, upgraded_hash: str | None) -> None:
    if upgraded_hash:
        user.password = upgraded_hash
        db.commit()
        db.refresh(user)


def _authenticate_user_record(user: User | None, password: str, db) -> User | None:
    if user is None or user.password is None:
        verify_password(password, DUMMY_HASH)
        return None
    verified, upgraded_hash = verify_password(password, user.password)
    if not verified:
        return None
    _persist_password_upgrade(db, user, upgraded_hash)
    return user


def authenticate_by_email(email: str, password: str, db) -> User | None:
    user = UserRepository.get_by_email(db, email)
    return _authenticate_user_record(user, password, db)


def authenticate_by_username_or_email(username_or_email: str, password: str, db) -> User | None:
    if "@" in username_or_email:
        return authenticate_by_email(username_or_email, password, db)
    user = UserRepository.get_by_username(db, username_or_email)
    return _authenticate_user_record(user, password, db)


def authenticate_user(payload, db):
    user = authenticate_by_email(payload.email, payload.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
