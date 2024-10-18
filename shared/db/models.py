from sqlalchemy import Column, Integer, String, Boolean

from shared.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
