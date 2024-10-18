# shared/services/user_service.py
from shared.db.repositories.user_repository import UserRepository
from shared.db.models import User
from shared.db.schemas.user import UserCreate, UserUpdate
from shared.core.security import auth

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user_data: UserCreate) -> User:
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=auth.get_password_hash(user_data.password)
        )
        return await self.user_repository.create(user)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repository.get_by_id(user_id)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        user = await self.user_repository.get_by_id(user_id)
        if user:
            for field, value in user_data.dict(exclude_unset=True).items():
                setattr(user, field, value)
            user = await self.user_repository.update(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        user = await self.user_repository.get_by_id(user_id)
        if user:
            await self.user_repository.delete(user)
            return True
        return False

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.user_repository.list(skip, limit)

