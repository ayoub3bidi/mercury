from typing import Optional
from pydantic import BaseModel

class UserRegisterSchema(BaseModel):
    username: Optional[str] = None
    email: str
    password: str

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