from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.security import create_access_token
from database.postgres_db import get_db
from jose import jwt
from models.User import User
from controllers.oidc.google import get_user_infos_from_google_token_url, get_user_infos_from_google_token, create_user
from constants.environment_variables import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    OIDC_GOOGLE_CLIENT_ID,
    OIDC_GOOGLE_CLIENT_SECRET,
    OIDC_GOOGLE_REDIRECT_URI,
    GOOGLE_AUTH_URL,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/google/login")
async def login_google():
    params = {
        "response_type": "code",
        "client_id": OIDC_GOOGLE_CLIENT_ID,
        "redirect_uri": OIDC_GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    authorization_url = f"{GOOGLE_AUTH_URL}?{query_string}"
    
    return {"url": authorization_url}

@router.get("/google")
async def auth_google(code: str = None, credential: str = None, db: Session = Depends(get_db)):
    if code:
        check = get_user_infos_from_google_token_url(code)
        if check['status'] is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")
        
        user_infos = check['user_infos']
    elif credential:
        check = get_user_infos_from_google_token(credential)
        if check['status'] is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credential")
        
        user_infos = check['user_infos']
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Neither code nor credential provided.")

    user = db.query(User).filter(User.oidc_configs.contains([{ "provider": "google", "id": user_infos['id'] }])).first()

    if not user:
        check = create_user(user_infos, db)
        if check['status'] is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check["message"])
        user = check['user']
        

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return { "token": access_token }

@router.get("/google/token")
async def get_google_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, OIDC_GOOGLE_CLIENT_SECRET, algorithms=["HS256"])
