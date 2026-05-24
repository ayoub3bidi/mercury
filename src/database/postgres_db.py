import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool

from utils.common import get_env_int

postgres_url = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

dbEngine = create_engine(
    postgres_url,
    echo=False,
    poolclass=QueuePool,
    pool_size=get_env_int("POSTGRES_SIZE_POOL", 30),
    max_overflow=get_env_int("POSTGRES_MAX_OVERFLOW", 10),
    pool_timeout=get_env_int("POSTGRES_POOL_TIMEOUT", 30),
    pool_recycle=get_env_int("POSTGRES_POOL_RECYCLE", 1800),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=dbEngine)

class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
