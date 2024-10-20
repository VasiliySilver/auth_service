from shared.db.repositories.user_repository import UserRepository
from shared.db.schemas.user import UserCreate, UserCreateInDB, UserResponse
from shared.core.security import auth


class AuthService:
    def __init__(self, db_session):
        self.user_repository = UserRepository(db_session)

    async def register_user(self, user: UserCreate) -> UserResponse:
        existing_user = await self.user_repository.get_by_email(user.email)
        if existing_user:
            raise ValueError("Unable to register user with provided information")

        hashed_password = auth.get_password_hash(user.password)
        new_user = await self.user_repository.create(
            UserCreateInDB(
                email=user.email,
                hashed_password=hashed_password,
                username=user.username,
            )
        )
        return UserResponse.model_validate(new_user)

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repository.get_by_email(email)
        if not user or not auth.verify_password(password, user.hashed_password):
            return None
        access_token = auth.create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
