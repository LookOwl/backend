from infrastructure.database.connection import async_session_factory

async def async_get_db_session():
    async with async_session_factory() as session:
        yield session


async def async_get_redis_session():
    pass