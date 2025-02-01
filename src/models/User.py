from database.postgres_db import Base
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL

class User(Base):
    __tablename__ = 'user'
    id = Column(GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)
    username = Column(String, nullable=True, default="")
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=True, default=False)
    disabled = Column(Boolean, nullable=True, default=False)
    oidc_configs = Column(JSONB, default=lambda: [], nullable=False)