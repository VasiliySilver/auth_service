from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db.session import get_db
from shared.db.repositories.user_repository import UserRepository
from services.user_service.service import UserService

def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db)

def get_user_service(user_repository: UserRepository = Depends(get_user_repository)):
    return UserService(user_repository)

