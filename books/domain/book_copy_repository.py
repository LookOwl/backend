from abc import ABC, abstractmethod

from books.domain.book_copy import BookCopy, BookCopyId
from books.domain.book import  BookId

class BookCopyRepository(ABC):

    @abstractmethod
    async def get_by_id(self, copy_id : BookCopyId) -> BookCopy | None:
        pass

    @abstractmethod
    async def count_available_copies_per_book(self, book_id : BookId) -> int:
        pass

    @abstractmethod
    async def find_by_book(self, id : BookId) -> list[BookCopy]:
        pass

    @abstractmethod
    async def save_book_copy(self, book_copy : BookCopy) -> None:
        pass

    @abstractmethod
    async def update_book_copy(self, book_copy : BookCopy) -> None:
        pass

    @abstractmethod
    async def delete_book_copy(self, book_copy : BookCopyId) -> None:
        pass
