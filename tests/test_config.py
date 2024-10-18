from shared.core.config import Settings

class TestSettings(Settings):
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    TESTING: bool = True
    SECRET_KEY: str = "test-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 
    
    class Config:
        env_file = ".env.test"

test_settings = TestSettings()