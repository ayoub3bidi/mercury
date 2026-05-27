from uuid import UUID

from sqlalchemy.orm import Query, Session

from models.User import User


class UserRepository:
    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: str | UUID) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_google_oidc_id(db: Session, google_id: str) -> User | None:
        return (
            db.query(User)
            .filter(User.oidc_configs.contains([{"provider": "google", "id": google_id}]))
            .first()
        )

    @staticmethod
    def list_all(db: Session) -> list[User]:
        return db.query(User).all()

    @staticmethod
    def filter_by_id(db: Session, user_id: str | UUID) -> Query:
        return db.query(User).filter(User.id == user_id)

    @staticmethod
    def create(db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()
