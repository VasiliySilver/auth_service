import pytest
import time
from shared.db.repositories.user_repository import UserRepository
from shared.db.schemas.user import UserCreateInDB, UserCreate
from shared.core.security import auth


@pytest.mark.asyncio
async def test_login_user(db_session, client):
    user_repo = UserRepository(db_session)
    password = "loginpassword123"
    hashed_password = auth.get_password_hash(password)
    user_data = UserCreateInDB(
        username="loginuser",
        email="loginuser@example.com",
        hashed_password=hashed_password,
    )
    await user_repo.create(user_data)

    form_data = {
        "username": "loginuser@example.com",
        "password": password,
    }
    login_response = await client.post("/auth/login", data=form_data)

    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    assert "access_token" in login_response.json()


@pytest.mark.asyncio
async def test_register_user(db_session, client):
    user_repo = UserRepository(db_session)
    password = "loginpassword123"
    user_data = UserCreate(
        username="loginuser", email="loginuser@example.com", password=password
    )

    # Вариант 1: отправка JSON данных
    json_data = {
        "username": user_data.username,
        "email": user_data.email,
        "password": user_data.password,
    }
    response = await client.post("/auth/register", json=json_data)

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 201, f"Registration failed: {response.text}"
    user_response = response.json()
    assert user_response["email"] == user_data.email
    assert user_response["username"] == user_data.username
    assert "id" in user_response

    # Verify user was actually created in the database
    db_user = await user_repo.get_by_email(user_data.email)
    assert db_user is not None
    assert db_user.email == user_data.email
    assert db_user.username == user_data.username


@pytest.mark.asyncio
async def test_register_user_duplicate_email(db_session, client):
    user_data = UserCreate(
        username="existinguser",
        email="existing@example.com",
        password="strongpassword123",
    )

    # Register the user first time
    await client.post("/auth/register", json=user_data.model_dump())

    # Try to register again with the same email
    response = await client.post("/auth/register", json=user_data.model_dump())

    assert (
        response.status_code == 400
    ), "Expected registration to fail for duplicate email"
    assert (
        "Unable to register user with provided information" in response.json()["detail"]
    )


@pytest.mark.asyncio
async def test_refresh_token(db_session, client):
    # Создаем пользователя
    user_repo = UserRepository(db_session)
    password = "refreshpassword123"
    hashed_password = auth.get_password_hash(password)
    user_data = UserCreateInDB(
        username="refreshuser",
        email="refreshuser@example.com",
        hashed_password=hashed_password,
    )
    await user_repo.create(user_data)

    # Логинимся, чтобы получить начальный токен
    login_data = {
        "username": "refreshuser@example.com",
        "password": password,
    }
    login_response = await client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200

    initial_token = login_response.json()["access_token"]

    # Добавляем небольшую задержку перед обновлением токена
    time.sleep(1)

    # Используем полученный токен для запроса на обновление
    headers = {"Authorization": f"Bearer {initial_token}"}
    refresh_response = await client.post("/auth/refresh", headers=headers)

    assert (
        refresh_response.status_code == 200
    ), f"Token refresh failed: {refresh_response.text}"
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert refresh_data["token_type"] == "bearer"

    # Проверяем, что новый токен отличается от исходного
    assert (
        refresh_data["access_token"] != initial_token
    ), "Refreshed token should be different from the initial token"

    # Проверяем, что новый токен действителен
    new_token_headers = {"Authorization": f"Bearer {refresh_data['access_token']}"}
    user_response = await client.get("/api/users/me", headers=new_token_headers)

    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data["email"] == "refreshuser@example.com"
