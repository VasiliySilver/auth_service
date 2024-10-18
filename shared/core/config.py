from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "auth_service"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@127.0.0.1:5432/mydatabase"
    SECRET_KEY: str = "your-secret-key"  # В продакшене используйте надежный секретный ключ
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней
       
    class Config:
        env_file = ".env"

settings = Settings()