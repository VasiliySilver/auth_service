import pytest
from httpx import AsyncClient
from services.service_gateway.main import app
from tests.test_config import test_settings


@pytest.mark.asyncio
async def test_login_user(db_session):
    app.state.settings = test_settings  # Ensure the app uses test settings

    # First, register a user
    async with AsyncClient(app=app, base_url="http://test") as ac:
        register_response = await ac.post("/auth/register", json={
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "loginpassword123"
        })
    
    assert register_response.status_code == 201, f"Failed to register user: {register_response.text}"

    # Then attempt to login
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_response = await ac.post("/auth/login", json={
            "email": "loginuser@example.com",
            "password": "loginpassword123"
        })
    
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    assert "access_token" in login_response.json()
