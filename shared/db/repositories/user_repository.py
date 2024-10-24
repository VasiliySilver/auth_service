# shared/repositories/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.db.models import User
from shared.db.schemas.user import UserCreateInDB, UserUpdateInDB
from typing import List, Optional


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreateInDB) -> User:
        existing_user = await self.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        db_user = User(**user_data.model_dump())
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).filter(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.session.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(
        self, user_id: int, user_data: UserUpdateInDB, full_update: bool = False
    ) -> User | None:
        user = await self.get_by_id(user_id)
        if user:
            if full_update:
                for key, value in user_data.model_dump(exclude_unset=True).items():
                    setattr(user, key, value)
            else:
                for key, value in user_data.model_dump(exclude_unset=True).items():
                    if value is not None:
                        setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return True
        return False
