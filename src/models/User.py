import uuid
from database.postgres_db import Base
from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL

class User(Base):
    __tablename__ = 'user'
    id = Column(GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    username = Column(String, nullable=True, default="")
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=True, default=False)
    disabled = Column(Boolean, nullable=True, default=False)