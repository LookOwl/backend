

from abc import ABC, abstractmethod


class UnitOfWork(ABC):

    async def __aenter__(self)-> "UnitOfWork":
        await self.begin()
        return self
    
    async def __aexit__(self, exc_type, exc, tb) -> None: # type: ignore
        if exc_type:
            try:
                await self.rollback()
            except Exception:
                raise Exception("Cannot rollback")
        else:
            try:
                await self.commit()
            except Exception as e1:
                try:
                    await self.rollback()
                except Exception as e2:
                    raise Exception("Cannot rollback") from e2
                raise Exception("Cannot commit") from e1

    @abstractmethod
    async def begin(self)->None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self)-> None:
        pass