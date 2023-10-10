import re
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union
from jose import jwt
from fastapi import HTTPException, status
from constants.environment_variables import ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME, JWT_ALGORITHM, JWT_SECRET_KEY
from models.User import User
from database.postgres_db import SessionLocal
from constants.regex import email_regex, password_regex

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
db = SessionLocal()

def create_admin_user():
    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not user:
        password = get_password_hash(ADMIN_PASSWORD)
        new_user = User(username=ADMIN_USERNAME, email=ADMIN_EMAIL, password=password, is_admin=True)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  

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