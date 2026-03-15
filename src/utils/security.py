import re
from datetime import datetime, timedelta
from typing import Union

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from constants.environment_variables import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)
from constants.regex import email_regex, password_regex
from models.User import User

crypting_algorithm = "sha256_crypt" if JWT_ALGORITHM == "HS256" else "bcrypt"

pwd_context = CryptContext(schemes=[crypting_algorithm], deprecated="auto")


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
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def authenticate_user(payload, db):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    if not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password")
    return user