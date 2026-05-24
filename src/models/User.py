import uuid

from sqlalchemy import Boolean, Column, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from database.postgres_db import Base


class User(Base):
    __tablename__ = "user"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
        default=uuid.uuid4,
    )
    username = Column(String, nullable=True, default="")
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)
    is_admin = Column(Boolean, nullable=True, default=False)
    disabled = Column(Boolean, nullable=True, default=False)
    oidc_configs = Column(JSONB, default=list, nullable=False)
