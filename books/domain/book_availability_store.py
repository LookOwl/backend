
from abc import ABC, abstractmethod

from books.domain.book import BookId
from books.domain.book_availability import BookAvailability


class BookAvailabilityStore(ABC):
    
    @abstractmethod
    async def get_availability(self, book_id : BookId) -> BookAvailability:
        pass

    @abstractmethod
    async def soft_reserve(self, book_id: BookId ) -> None:
        pass

    @abstractmethod
    async def soft_release(self, book_id : BookId) -> None:
        pass
    
    @abstractmethod
    async def hard_reserve(self, book_id : BookId) -> None:
        pass
    
    @abstractmethod
    async def hard_release(self, book_id : BookId) -> None:
        pass