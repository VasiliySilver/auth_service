from sqlalchemy.ext.asyncio import create_async_engine
from shared.core.config import settings
from sqlalchemy.orm import declarative_base


Base = declarative_base()


def get_engine(test_mode=False):
    if test_mode:
        # Используем SQLite в памяти для тестов
        return create_async_engine(
            "sqlite+aiosqlite:///:memory:", echo=True, future=True
        )
    else:
        return create_async_engine(settings.DATABASE_URL, echo=True, future=True)


engine = get_engine()
