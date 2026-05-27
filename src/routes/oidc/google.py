from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.security import create_access_token
from database.postgres_db import get_db
from jose import jwt
from repositories.user import UserRepository
from controllers.oidc.google import get_user_infos_from_google_token_url, get_user_infos_from_google_token, create_user
from constants.settings import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/google/login")
async def login_google():
    params = {
        "response_type": "code",
        "client_id": settings.OIDC_GOOGLE_CLIENT_ID,
        "redirect_uri": settings.OIDC_GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    authorization_url = f"{settings.GOOGLE_AUTH_URL}?{query_string}"

    return {"url": authorization_url}


@router.get("/google")
async def auth_google(code: str = None, credential: str = None, db: Session = Depends(get_db)):
    if code:
        check = get_user_infos_from_google_token_url(code)
        if check["status"] is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")

        user_infos = check["user_infos"]
    elif credential:
        check = get_user_infos_from_google_token(credential)
        if check["status"] is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credential")

        user_infos = check["user_infos"]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Neither code nor credential provided.")

    user = UserRepository.get_by_google_oidc_id(db, user_infos["id"])

    if not user:
        check = create_user(user_infos, db)
        if check["status"] is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check["message"])
        user = check["user"]

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"token": access_token}


@router.get("/google/token")
async def get_google_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.JWT_ALGORITHM])
