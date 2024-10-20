# shared/services/user_service.py
from shared.db.repositories.user_repository import UserRepository
from shared.db.models import User
from shared.db.schemas.user import UserCreate, UserUpdate, UserUpdateInDB
from shared.core.security import auth


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user_data: UserCreate) -> User:
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=auth.get_password_hash(user_data.password),
        )
        return await self.user_repository.create(user)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repository.get_by_id(user_id)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        update_data = UserUpdateInDB(**user_data.model_dump(exclude_unset=True))
        return await self.user_repository.update(user_id, update_data)

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repository.delete(user_id)

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.user_repository.list(skip, limit)
