from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from database.postgres_db import get_db
import os
from models.User import User
from schemas.User import UserLoginSchema, UserSchema
from utils.security import create_access_token, get_password_hash, verify_password


router = APIRouter()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

def authenticate_user(payload, db):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    if not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password")
    return user

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: UserSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    payload.password = get_password_hash(payload.password)
    new_user = User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user": new_user}

@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(payload: UserLoginSchema, db: Session = Depends(get_db)):
    user = authenticate_user(payload, db)
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"user": user, "token": {"access_token": access_token, "token_type": "bearer"}}