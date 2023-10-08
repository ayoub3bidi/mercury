from typing import Optional
from pydantic import BaseModel

class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class UserSchema(BaseModel):
    id: int
    username: Optional[str] = None
    email: str
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        
class UserAdminRegisterSchema(BaseModel):
    username: Optional[str] = None
    email: str
    password: str
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        
class UserAdminUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class UserRegisterSchema(BaseModel):
    username: Optional[str] = None
    email: str
    password: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        
class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True