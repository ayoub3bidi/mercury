from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

_orm_config = ConfigDict(
    from_attributes=True,
    populate_by_name=True,
    arbitrary_types_allowed=True,
)


class UserLoginSchema(BaseModel):
    model_config = _orm_config
    email: str
    password: str


class UserSchema(BaseModel):
    model_config = _orm_config
    id: UUID
    username: Optional[str] = None
    email: str
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserAdminRegisterSchema(BaseModel):
    model_config = _orm_config
    username: Optional[str] = None
    email: str
    password: str
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserAdminUpdateSchema(BaseModel):
    model_config = _orm_config
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserRegisterSchema(BaseModel):
    model_config = _orm_config
    username: Optional[str] = None
    email: str
    password: str


class UserUpdateSchema(BaseModel):
    model_config = _orm_config
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
