from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db.models import User, UserRole
from shared.db.schemas.user import UserResponse, UserUpdate
from shared.db.session import get_db
from services.user_service.service import UserService
from shared.core.security import get_current_user_with_roles, auth
from services.user_service.dependencies import get_user_service
from shared.db.repositories.user_repository import UserRepository

router = APIRouter(dependencies=[Depends(auth.get_current_user)])

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(auth.get_current_active_user)
):
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user_with_roles(UserRole.ADMIN)),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_roles(UserRole.ADMIN))
):
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    users = await user_service.list_users(skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_roles(UserRole.ADMIN))
):
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    updated_user = await user_service.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_with_roles(UserRole.ADMIN))
):
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
