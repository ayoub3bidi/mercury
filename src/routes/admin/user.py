from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter
from controllers.admin.user import add_user
from database.postgres_db import get_db
from middleware.auth_guard import get_current_admin_user
from models.User import User
from schemas.User import UserSchema, UserAdminRegisterSchema
from utils.filter import remove_password_from_users, remove_password_from_user

router = APIRouter()

@router.get("/all", status_code=status.HTTP_200_OK)
def get_all_users(current_user: Annotated[UserSchema, Depends(get_current_admin_user)], db: Session = Depends(get_db)):
    users = db.query(User).all()
    return remove_password_from_users(users)

@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(current_user: Annotated[UserSchema, Depends(get_current_admin_user)], user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return remove_password_from_user(user)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(current_user: Annotated[UserSchema, Depends(get_current_admin_user)], payload: UserAdminRegisterSchema, db: Session = Depends(get_db)):
    return add_user(payload, db)