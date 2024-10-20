from typing import List
from sqlalchemy import Integer, String, Boolean, JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum

from shared.db.database import Base


class UserRole(PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    roles: Mapped[List[str]] = mapped_column(
        MutableList.as_mutable(JSON()), default=[UserRole.USER.value]
    )

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}', roles={self.roles})"

    @classmethod
    def __declare_last__(cls):
        from sqlalchemy import event

        @event.listens_for(cls, "load")
        def receive_load(instance, context):
            if isinstance(instance.roles, list):
                instance.roles = [
                    UserRole(role) for role in instance.roles if isinstance(role, str)
                ]
