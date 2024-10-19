import pytest
from shared.db.models import User, UserRole
from shared.db.repositories.user_repository import UserRepository
from shared.db.schemas.user import UserCreateInDB, UserUpdateInDB
from sqlalchemy import delete

@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(username="testuser1", email="test1@example.com", hashed_password="hashed_password", roles=[UserRole.USER.value])
    db_session.add(user)
    await db_session.commit()
    
    result = await db_session.get(User, user.id)
    assert result.username == "testuser1"
    assert result.email == "test1@example.com"

@pytest.mark.asyncio
async def test_user_representation(db_session):
    user = User(username="testuser2", email="test2@example.com", hashed_password="hashed_password", roles=["user"])
    db_session.add(user)
    await db_session.commit()
    
    assert str(user) == f"User(id={user.id}, username='testuser2', email='test2@example.com', roles=['user'])"

@pytest.mark.asyncio
async def test_user_repository_create(db_session):
    user_repo = UserRepository(db_session)
    user_data = UserCreateInDB(username="newuser", email="newuser@example.com", hashed_password="hashed_password", roles=[UserRole.USER.value])
    
    new_user = await user_repo.create(user_data)
    
    assert new_user.id is not None
    assert new_user.username == "newuser"
    assert new_user.email == "newuser@example.com"

@pytest.mark.asyncio
async def test_user_repository_get_by_id(db_session):
    user_repo = UserRepository(db_session)
    user_data = UserCreateInDB(username="getbyid", email="getbyid@example.com", hashed_password="hashed_password", roles=[UserRole.USER.value])
    new_user = await user_repo.create(user_data)
    
    retrieved_user = await user_repo.get_by_id(new_user.id)
    
    assert retrieved_user is not None
    assert retrieved_user.id == new_user.id
    assert retrieved_user.username == "getbyid"

@pytest.mark.asyncio
async def test_user_repository_get_by_username(db_session):
    user_repo = UserRepository(db_session)
    user_data = UserCreateInDB(username="getbyusername", email="getbyusername@example.com", hashed_password="hashed_password", roles=[UserRole.USER.value])
    await user_repo.create(user_data)
    
    retrieved_user = await user_repo.get_by_username("getbyusername")
    
    assert retrieved_user is not None
    assert retrieved_user.username == "getbyusername"

@pytest.mark.asyncio
async def test_user_repository_get_by_email(db_session):
    user_repo = UserRepository(db_session)
    user_data = UserCreateInDB(username="getbyemail", email="getbyemail@example.com", hashed_password="hashed_password", roles=[UserRole.USER.value])
    await user_repo.create(user_data)
    
    retrieved_user = await user_repo.get_by_email("getbyemail@example.com")
    
    assert retrieved_user is not None
    assert retrieved_user.email == "getbyemail@example.com"

@pytest.mark.asyncio
async def test_user_repository_update(db_session):
    user_repo = UserRepository(db_session)
    user_data = UserCreateInDB(username="updateuser", email="updateuser@example.com", hashed_password="hashed_password", roles=[UserRole.USER.value])
    new_user = await user_repo.create(user_data)

    update_data = UserUpdateInDB(username="updatedusername")
    updated_user = await user_repo.update(new_user.id, update_data)
    
    assert updated_user is not None
    assert updated_user.username == "updatedusername"

@pytest.mark.asyncio
async def test_user_repository_delete(db_session):
    user_repo = UserRepository(db_session)
    user_data = UserCreateInDB(username="deleteuser", email="deleteuser@example.com", hashed_password="hashed_password", roles=[UserRole.USER.value])
    new_user = await user_repo.create(user_data)

    result = await user_repo.delete(new_user.id)
    assert result is True

    deleted_user = await user_repo.get_by_id(new_user.id)
    assert deleted_user is None

@pytest.mark.asyncio
async def test_user_repository_list(db_session):
    # Clear the database first
    await db_session.execute(delete(User))
    await db_session.commit()

    user_repo = UserRepository(db_session)
    for i in range(5):
        user_data = UserCreateInDB(username=f"listuser{i}", email=f"listuser{i}@example.com", hashed_password="hashed_password", roles=[UserRole.USER.value])
        await user_repo.create(user_data)
    
    users = await user_repo.list(skip=1, limit=3)
    
    assert len(users) == 3
    assert users[0].username == "listuser1"
    assert users[-1].username == "listuser3"
