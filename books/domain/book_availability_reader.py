
from abc import ABC, abstractmethod

from books.domain.book import BookId
from books.domain.book_availability import BookAvailability


class BookAvailabilityReader(ABC):
    
    @abstractmethod
    async def get_availability(self, book_id : BookId) -> BookAvailability:
        pass
