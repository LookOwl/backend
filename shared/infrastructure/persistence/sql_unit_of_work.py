from sqlalchemy.ext.asyncio import AsyncSession
from shared.application.unit_of_work import UnitOfWork


class SQLUnitOfWork(UnitOfWork):
    
    async_session : AsyncSession

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.async_session = session

    async def begin(self)->None:
        await self.async_session.begin()
        return
    
    async def commit(self) -> None:
        await self.async_session.commit()
        return
    
    async def rollback(self)-> None:
        await self.async_session.rollback() 
        return