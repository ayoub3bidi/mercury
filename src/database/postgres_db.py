import os
from utils.common import get_env_int
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

postgres_db_name = os.getenv("POSTGRES_DB")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_pool_size = get_env_int("POSTGRES_SIZE_POOL", 30)
postgres_max_overflow = get_env_int("POSTGRES_MAX_OVERFLOW", 10)
postgres_pool_timeout = get_env_int("POSTGRES_POOL_TIMEOUT", 30)
postgres_pool_recycle = get_env_int("POSTGRES_POOL_RECYCLE", 1800)

POSTGRES_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db_name}"

dbEngine = create_engine(
    POSTGRES_URL,
    echo=False,
    poolclass=QueuePool,
    pool_size=postgres_pool_size,
    max_overflow=postgres_max_overflow,
    pool_timeout=postgres_pool_timeout,
    pool_recycle=postgres_pool_recycle,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=dbEngine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database error occurred: {e}")
    finally:
        db.close()
