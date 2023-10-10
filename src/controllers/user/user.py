from datetime import timedelta
import os
from fastapi import HTTPException, status
from constants.environment_variables import ACCESS_TOKEN_EXPIRE_MINUTES
from models.User import User
from utils.security import authenticate_user, create_access_token, get_password_hash, validate_email, validate_password
from utils.variables import is_not_empty

def register(payload, db):
    if (validate_email(payload.email) == False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")
    if (validate_password(payload.password) == False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    payload.password = get_password_hash(payload.password)
    new_user = User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
            "id": new_user.id,
            "email": new_user.email
        }
    
def login(payload, db):
    user = authenticate_user(payload, db)
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {
        "id": user.id,
        "email": user.email,
        "token": {
            "access_token": access_token, 
            "token_type": "bearer"
        }
    }
    
def update_user(current_user, payload, db):
    user = db.query(User).filter(User.id == current_user.id)
    
    existing_user = user.first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    updated_user = User(**payload.dict())
    
    if is_not_empty(updated_user.email) and updated_user.email != existing_user.email:
        user_exists = db.query(User).filter(User.email == updated_user.email).first()
        if user_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"The email {updated_user.email} already exists")

    if is_not_empty(updated_user.username) and updated_user.username != existing_user.username:
        user_exists = db.query(User).filter(User.username == updated_user.username).first()
        if user_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"The username {updated_user.username} already exists")
    
    if payload.username:
        user.update({"username": payload.username})
    if payload.email:
        user.update({"email": payload.email})
    if payload.password:
        user.update({"password": get_password_hash(payload.password)})

    return {
        "message": "your account has been updated successfully"
    }