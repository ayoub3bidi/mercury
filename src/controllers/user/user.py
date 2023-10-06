from datetime import timedelta
import os
from fastapi import HTTPException, status
from models.User import User
from utils.security import authenticate_user, create_access_token, get_password_hash, validate_email, validate_password

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

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