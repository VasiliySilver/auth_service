from fastapi import APIRouter
from services.auth_service.api.routes import router as auth_router
from services.user_service.api.routes import router as user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/api/users", tags=["users"])
