from fastapi import HTTPException, status
from models.User import User
from utils.security import get_password_hash
from utils.variables import is_not_empty


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
    
def update_user(user_id, payload, db):
    user = db.query(User).filter(User.id == user_id)
    
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
    if payload.is_admin != None:
        user.update({"is_admin": payload.is_admin})
    if payload.disabled != None:
        User.disabled = user.disabled
        user.update({"disabled": payload.disabled})

    return {
        "message": "user been updated successfully"
    }
    
def delete_user(user_id, db):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {
        "message": "user been deleted successfully"
    }