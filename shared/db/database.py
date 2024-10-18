from sqlalchemy.ext.asyncio import create_async_engine
from shared.core.config import settings
from sqlalchemy.orm import declarative_base


Base = declarative_base()

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)