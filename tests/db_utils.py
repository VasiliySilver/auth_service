import asyncio
import asyncpg
from tests.test_config import test_settings

async def create_test_database():
    sys_conn = await asyncpg.connect(
        database='postgres',
        user=test_settings.POSTGRES_USER,
        password=test_settings.POSTGRES_PASSWORD,
        host=test_settings.POSTGRES_HOST,
        port=test_settings.POSTGRES_PORT
    )
    await sys_conn.execute(f'CREATE DATABASE {test_settings.POSTGRES_DB}')
    await sys_conn.close()

async def drop_test_database():
    sys_conn = await asyncpg.connect(
        database='postgres',
        user=test_settings.POSTGRES_USER,
        password=test_settings.POSTGRES_PASSWORD,
        host=test_settings.POSTGRES_HOST,
        port=test_settings.POSTGRES_PORT
    )
    await sys_conn.execute(f'DROP DATABASE IF EXISTS {test_settings.POSTGRES_DB}')
    await sys_conn.close()

def run_async(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

