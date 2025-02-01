from sqlalchemy.orm.attributes import flag_modified
from models.User import User

def update_oidc_info(user_id: int, provider: str, id: str, email: str, db):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if not isinstance(user.oidc_configs, list):
            user.oidc_configs = []
        
        #? Remove existing config for this provider if it exists
        user.oidc_configs = [
            config for config in user.oidc_configs
            if not (config.get("provider") == provider and "id" in config)
        ]

        user.oidc_configs.append({
            "provider": provider,
            "id": id,
            "email": email
        })

        flag_modified(user, "oidc_configs")
        db.commit()

        return True
