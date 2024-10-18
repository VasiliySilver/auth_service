# shared/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    password: str
    
class UserCreateInDB(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    hashed_password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None