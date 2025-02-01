import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from models.User import User
from utils.oidc import update_oidc_info
from constants.environment_variables import (
    OIDC_GOOGLE_CLIENT_ID,
    OIDC_GOOGLE_CLIENT_SECRET,
    OIDC_GOOGLE_REDIRECT_URI,
    GOOGLE_TOKEN_URL,
    GOOGLE_USER_INFO_URL,
    HTTP_REQUEST_TIMEOUT
)

def get_user_infos_from_google_token_url(code):
    token_data = {
        "code": code,
        "client_id": OIDC_GOOGLE_CLIENT_ID,
        "client_secret": OIDC_GOOGLE_CLIENT_SECRET,
        "redirect_uri": OIDC_GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data, timeout=HTTP_REQUEST_TIMEOUT)
    access_token = token_response.json().get("access_token")
    
    user_infos_response = requests.get(GOOGLE_USER_INFO_URL, headers={"Authorization": f"Bearer {access_token}"}, timeout=HTTP_REQUEST_TIMEOUT)
    user_infos = user_infos_response.json()

    if not user_infos:
        return {
            "status": False,
            "user_infos": user_infos
        }
    
    return {
        "status": True,
        "user_infos": user_infos
    }

def get_user_infos_from_google_token(id_token_str):
    id_info = id_token.verify_oauth2_token(id_token_str, google_requests.Request(), OIDC_GOOGLE_CLIENT_ID)
    user_id = id_info['sub']
    email = id_info.get('email')
    
    user_infos = {
        'id': user_id,
        'email': email,
    }
    
    if not user_infos:
        return {
            "status": False,
            "user_infos": user_infos
        }
    
    return {
        "status": True,
        "user_infos": user_infos
    }


def create_user(user_infos, db):
    user_exists = db.query(User).filter(User.email == user_infos['email']).first()

    if user_exists:
        got_updated = update_oidc_info(
            user_exists.id,
            'google',
            user_infos['id'],
            user_infos['email'],
            db
        )
        if got_updated is False:
            return {
                "status": False,
                "message": "Failed to update user"
            }

        return {
            "status": True,
            "user": user_exists
        }

    new_user = User(
        email=user_infos['email'],
        oidc_configs=[{
            "provider": "google",
            "id": user_infos['id'],
            "email": user_infos['email']
        }]
    )
    new_user.save(db)
    return {
        "status": True,
        "user": new_user
    }
