from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.ext.mutable import MutableList
from enum import Enum as PyEnum

from shared.db.database import Base


class UserRole(PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    roles = Column(MutableList.as_mutable(JSON), default=[UserRole.USER.value])

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}', roles={self.roles})"

    @classmethod
    def __declare_last__(cls):
        from sqlalchemy import event

        @event.listens_for(cls, 'load')
        def receive_load(instance, context):
            if isinstance(instance.roles, list):
                instance.roles = [UserRole(role) for role in instance.roles if isinstance(role, str)]
