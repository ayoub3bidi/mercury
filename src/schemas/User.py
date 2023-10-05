from typing import Optional
from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    is_admin: Optional[bool] = False
    disabled: Optional[bool] = False

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class UserResponse(BaseModel):
    status: str
    user: UserSchema