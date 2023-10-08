from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter
from controllers.user.user import register, login, update_user
from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from schemas.User import UserLoginSchema, UserRegisterSchema, UserUpdateSchema
from utils.filter import remove_password_from_user

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterSchema, db: Session = Depends(get_db)):
    return register(payload, db)

@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(payload: UserLoginSchema, db: Session = Depends(get_db)):
    return login(payload, db)

@router.get("", status_code=status.HTTP_200_OK)
def get_current_user_data(current_user: UserLoginSchema = Depends(get_current_active_user)):
    return remove_password_from_user(current_user)

@router.patch("", status_code=status.HTTP_200_OK)
def update_current_user_data(payload: UserUpdateSchema, current_user: UserLoginSchema = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return update_user(current_user, payload, db)