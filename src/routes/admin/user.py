from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter
from database.postgres_db import get_db
from middleware.auth_guard import get_current_admin_user
from models.User import User
from schemas.User import UserSchema
from utils.filter import remove_password_from_users

router = APIRouter()

@router.get("/user/all", status_code=status.HTTP_200_OK)
def get_all_users(current_user: Annotated[UserSchema, Depends(get_current_admin_user)], db: Session = Depends(get_db)):
    users = db.query(User).all()
    return remove_password_from_users(users)