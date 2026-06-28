from fastapi import Depends
from shared.infrastructure.persistence.sql_drivers import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from shared.infrastructure.persistence.sql_unit_of_work import SQLUnitOfWork

async def get_async_sql_session():
    async with async_session_factory() as session:
        yield session


def get_sql_unit_of_work(
    session : AsyncSession = Depends(get_async_sql_session)
):
    return SQLUnitOfWork(
        session
    )
