from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db.schemas.user import UserCreate, UserResponse
from shared.db.session import get_db
from services.auth_service.service import AuthService
from shared.core.security import auth
from shared.db.schemas.token import Token  # Add this import

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(form_data: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        return await auth_service.register_user(form_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    result = await auth_service.authenticate_user(
        form_data.username, form_data.password
    )

    if not result:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    return result


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: UserResponse = Depends(auth.get_current_user)):
    access_token = auth.create_access_token(data={"sub": current_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
