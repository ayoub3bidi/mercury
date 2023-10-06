import re
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union
from jose import jwt
from fastapi import HTTPException, status
from models.User import User
from database.postgres_db import SessionLocal

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$"

admin_username = os.getenv('ADMIN_USERNAME')
admin_email = os.getenv('ADMIN_EMAIL')
admin_password = os.getenv('ADMIN_PASSWORD')
db = SessionLocal()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

def create_admin_user():
    user = db.query(User).filter(User.email == admin_email).first()
    if not user:
        password = get_password_hash(admin_password)
        new_user = User(username=admin_username, email=admin_email, password=password, is_admin=True)
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
        expire = datetime.utcnow() + timedelta(minutes=15)
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