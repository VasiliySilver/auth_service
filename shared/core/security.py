from typing import Optional
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.session import get_db
from shared.db.repositories.user_repository import UserRepository
from shared.db.models import User, UserRole
from shared.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Auth:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        result = pwd_context.verify(plain_password, hashed_password)
        logging.debug(f"Password verification result: {result}")
        logging.debug(f"Plain password: {plain_password}")
        logging.debug(f"Hashed password: {hashed_password}")
        return result

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub", None)
            if username is None:
                raise ValueError("Missing username in token")
        except (jwt.PyJWTError, ValueError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

    @staticmethod
    async def get_current_active_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        user = await current_user  # Ожидаем завершения корутины
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user

auth = Auth()

import logging

logger = logging.getLogger(__name__)

def get_current_user_with_roles(*required_roles: UserRole):
    async def current_user_with_roles(
        current_user: User = Depends(auth.get_current_active_user),
    ) -> User:
        logger.info(f"Current user: id={current_user.id}, username={current_user.username}, email={current_user.email}")
        logger.info(f"Current user roles: {current_user.roles}")
        logger.info(f"Required roles: {required_roles}")
        
        # Преобразуем роли пользователя в объекты UserRole
        user_roles = [UserRole(role) for role in current_user.roles]
        
        has_required_role = any(role in user_roles for role in required_roles)
        logger.info(f"User has required role: {has_required_role}")
        
        if not has_required_role:
            logger.warning("User does not have required roles")
            raise HTTPException(
                status_code=403, detail="Not enough permissions"
            )
        return current_user
    return current_user_with_roles
