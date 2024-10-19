from fastapi.security import OAuth2PasswordRequestForm
import pytest
from shared.db.repositories.user_repository import UserRepository
from shared.db.schemas.user import UserCreateInDB
from shared.core.security import auth

@pytest.mark.asyncio
async def test_login_user(db_session, client):
    user_repo = UserRepository(db_session)
    password = "loginpassword123"
    hashed_password = auth.get_password_hash(password)
    user_data = UserCreateInDB(
        username="loginuser",
        email="loginuser@example.com",
        hashed_password=hashed_password
    )
    await user_repo.create(user_data)
    
    form_data = {
        "username": "loginuser@example.com",
        "password": password,
    }
    login_response = await client.post("/auth/login", data=form_data)
    
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    assert "access_token" in login_response.json()


# @pytest.mark.asyncio
# async def test_register_user(db_session, client):
#     user_data = UserCreateInDB(
#         username="newuser",
#         email="newuser@example.com",
#         hashed_password="strongpassword123"
#     )

#     response = await client.post("/auth/register", json=user_data.model_dump())

#     assert response.status_code == 201, f"Registration failed: {response.text}"
#     user_response = response.json()
#     assert user_response["email"] == user_data.email
#     assert user_response["username"] == user_data.username
#     assert "id" in user_response

#     # Verify user was actually created in the database
#     user_repo = UserRepository(db_session)
#     db_user = await user_repo.get_by_email(user_data.email)
#     assert db_user is not None
#     assert db_user.email == user_data.email
#     assert db_user.username == user_data.username


# @pytest.mark.asyncio
# async def test_register_user_duplicate_email(db_session, client):
#     user_data = UserCreateInDB(
#         username="existinguser",
#         email="existing@example.com",
#         hashed_password="strongpassword123"
#     )

#     # Register the user first time
#     await client.post("/auth/register", json=user_data.model_dump())

#     # Try to register again with the same email
#     response = await client.post("/auth/register", json=user_data.model_dump())

#     assert response.status_code == 400, "Expected registration to fail for duplicate email"
#     assert "Unable to register user with provided information" in response.json()["detail"]
