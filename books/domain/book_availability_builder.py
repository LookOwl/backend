from abc import ABC, abstractmethod
from books.domain.book import BookId


class BookAvailabilityBuilder(ABC):

    @abstractmethod
    async def build(self,book_id : BookId) -> None:
        pass