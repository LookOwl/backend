
from abc import ABC, abstractmethod

from books.domain.book import BookId
from books.domain.book_availability import BookAvailability


class BookAvailabilityCacheMiss(Exception):
    """Raised by a reader when the availability cache holds no entry for a book.

    Only this exception should trigger a rebuild; any other error (lock timeout,
    connection failure, ...) must propagate so it is not mistaken for a miss.
    """
    pass


class BookAvailabilityReader(ABC):

    @abstractmethod
    async def get_availability(self, book_id : BookId) -> BookAvailability:
        pass
