# shared/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    roles: List[UserRole] = Field(default=[UserRole.USER])

    @field_validator('roles', mode='before')
    @classmethod
    def ensure_list_of_roles(cls, v):
        if isinstance(v, str):
            return [UserRole(role.strip()) for role in v.split(',')]
        elif isinstance(v, (list, tuple)):
            return [UserRole(role) if isinstance(role, str) else role for role in v]
        return v

class UserCreate(UserBase):
    password: str

class UserCreateInDB(UserBase):
    hashed_password: str
    
class UserUpdateInDB(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    hashed_password: str | None = None
    is_active: bool | None = None
    roles: list[str] | None = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    roles: Optional[List[UserRole]] = None

    @field_validator('roles', mode='before')
    @classmethod
    def ensure_list_of_roles(cls, v):
        if isinstance(v, str):
            return [UserRole(role.strip()) for role in v.split(',')]
        elif isinstance(v, (list, tuple)):
            return [UserRole(role) if isinstance(role, str) else role for role in v]
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    is_active: bool | None = None
    roles: list[UserRole] | None = None

    class Config:
        from_attributes = True
