from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from shared.db.database import get_engine


def get_async_session_local(test_mode=False):
    engine = get_engine(test_mode)
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

AsyncSessionLocal = get_async_session_local()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

