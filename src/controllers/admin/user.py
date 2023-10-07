from fastapi import HTTPException, status
from models.User import User
from utils.security import get_password_hash


def add_user(payload, db):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    password_entered = payload.password
    payload.password = get_password_hash(payload.password)
    new_user = User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
            "id": new_user.id,
            "email": new_user.email,
            "password": password_entered
        }