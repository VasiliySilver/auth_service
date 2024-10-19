import pytest
from shared.db.repositories.user_repository import UserRepository
from shared.db.schemas.user import UserCreateInDB, UserUpdate, UserRole
from shared.core.security import auth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from sqlalchemy import delete
from shared.db.models import User  # Убедитесь, что путь импорта правильный

@pytest.fixture(autouse=True)
async def clear_users(db_session: AsyncSession):
    async with db_session.begin():
        await db_session.execute(delete(User))
    await db_session.commit()

@pytest.mark.asyncio
async def test_get_current_user(db_session, client):
    user_repo = UserRepository(db_session)
    password = "testpassword123"
    hashed_password = auth.get_password_hash(password)
    user_data = UserCreateInDB(
        username="testuser",
        email="testuser@example.com",
        hashed_password=hashed_password,
        roles=[UserRole.USER]
    )
    created_user = await user_repo.create(user_data)

    login_data = {"username": "testuser@example.com", "password": password}
    login_response = await client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == "testuser@example.com"
    assert user["username"] == "testuser"
    assert user["roles"] == [UserRole.USER]

@pytest.mark.asyncio
async def test_get_user(db_session, client):
    user_repo = UserRepository(db_session)

    # Очищаем базу данных от всех пользователей
    await db_session.execute(delete(User))
    await db_session.commit()

    # Создаем обычного пользователя
    user_password = "userpass"
    user_data = UserCreateInDB(
        username="testuser",
        email="testuser@example.com",
        hashed_password=auth.get_password_hash(user_password),
        roles=[UserRole.USER.value]
    )
    
    user = await user_repo.create(user_data)

    # Создаем админа
    admin_pass = "adminpass"
    admin_data = UserCreateInDB(
        username="testadmin",
        email="testadmin@example.com",
        hashed_password=auth.get_password_hash(admin_pass),
        roles=[UserRole.USER.value, UserRole.ADMIN.value]
    )
    admin = await user_repo.create(admin_data)

    # Логинимся как админ
    login_data = {"username": "testadmin@example.com", "password": admin_pass}
    login_response = await client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]

    # Получаем информацию о пользователе
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get(f"/api/users/{user.id}", headers=headers)

    # Проверяем результат
    assert response.status_code == 200
    assert response.json()["id"] == user.id
    assert response.json()["username"] == user.username

@pytest.mark.asyncio
async def test_get_all_users(db_session, client):
    # Создаем админа и нескольких пользователей
    user_repo = UserRepository(db_session)
    admin_data = UserCreateInDB(
        username="admin",
        email="admin@example.com",
        hashed_password=auth.get_password_hash("adminpass"),
        roles=[UserRole.ADMIN.value, UserRole.USER.value]
    )
    await user_repo.create(admin_data)

    for i in range(5):
        user_data = UserCreateInDB(
            username=f"user{i}",
            email=f"user{i}@example.com",
            hashed_password=auth.get_password_hash(f"userpass{i}"),
            roles=[UserRole.USER.value]
        )
        await user_repo.create(user_data)

    # Логинимся как админ
    login_data = {"username": "admin@example.com", "password": "adminpass"}
    login_response = await client.post("/auth/login", data=login_data)
    admin_token = login_response.json()["access_token"]

    # Получаем список всех пользователей
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/api/users/", headers=headers)

    assert response.status_code == 200
    users = response.json()
    assert len(users) == 6  # 5 обычных пользователей + 1 админ
    assert any(user["email"] == "admin@example.com" for user in users)
    assert all(f"user{i}@example.com" in [user["email"] for user in users] for i in range(5))

@pytest.mark.asyncio
async def test_update_user(db_session, client):
    # Создаем админа и пользователя
    user_repo = UserRepository(db_session)
    admin_data = UserCreateInDB(
        username="admin",
        email="admin@example.com",
        hashed_password=auth.get_password_hash("adminpass"),
        roles=["admin"]
    )
    await user_repo.create(admin_data)

    user_data = UserCreateInDB(
        username="user",
        email="user@example.com",
        hashed_password=auth.get_password_hash("userpass")
    )
    user = await user_repo.create(user_data)

    # Логинимся как админ
    login_data = {"username": "admin@example.com", "password": "adminpass"}
    login_response = await client.post("/auth/login", data=login_data)
    admin_token = login_response.json()["access_token"]

    # Обновляем пользователя
    headers = {"Authorization": f"Bearer {admin_token}"}
    update_data = UserUpdate(username="updateduser")
    response = await client.put(f"/api/users/{user.id}", headers=headers, json=update_data.model_dump())
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["username"] == "updateduser"

@pytest.mark.asyncio
async def test_delete_user(db_session, client):
    # Создаем админа и пользователя
    user_repo = UserRepository(db_session)
    admin_data = UserCreateInDB(
        username="admin",
        email="admin@example.com",
        hashed_password=auth.get_password_hash("adminpass"),
        roles=["admin"]
    )
    await user_repo.create(admin_data)

    user_data = UserCreateInDB(
        username="user",
        email="user@example.com",
        hashed_password=auth.get_password_hash("userpass")
    )
    user = await user_repo.create(user_data)

    # Логинимся как админ
    login_data = {"username": "admin@example.com", "password": "adminpass"}
    login_response = await client.post("/auth/login", data=login_data)
    admin_token = login_response.json()["access_token"]

    # Удаляем пользователя
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.delete(f"/api/users/{user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    # Проверяем, что пользователь действительно удален
    deleted_user = await user_repo.get_by_id(user.id)
    assert deleted_user is None
