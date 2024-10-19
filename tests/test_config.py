from typing import List
from shared.core.config import Settings

class TestSettings(Settings):
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    TESTING: bool = True
    SECRET_KEY: str = "test-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 
    
    # Add the missing fields
    db_echo: bool = True
    db_pool_size: int = 5
    db_max_overflow: int = 10
    debug: bool = True
    app_name: str = "TestApp"
    api_v1_str: str = "/api/v1"
    log_level: str = "DEBUG"
    backend_cors_origins: List[str] = ["http://localhost", "http://localhost:3000"]
    mock_external_api: bool = True
    test_user_email: str = "test@example.com"
    test_user_password: str = "test_password"
    
    class Config:
        env_file = ".env.test"
        extra = "ignore"  # This will ignore any extra fields not defined in the class

test_settings = TestSettings()
