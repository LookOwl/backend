from abc import ABC, abstractmethod
from books.domain.book import Book, BookId
from books.domain.book_search_criteria import AdvancedBookSearchCriteria, BookSearchCriteria
from books.domain.result_page import ResultPage

class BookRepository(ABC):
    
    @abstractmethod
    async def get_by_id(self, book_id : BookId) -> Book | None:
        pass
    
    @abstractmethod
    async def search_book(self, search_criteria: BookSearchCriteria, page_limits: ResultPage) -> list[Book]:
        pass

    @abstractmethod
    async def advanced_search_book(self, search_criteria: AdvancedBookSearchCriteria, page_limits: ResultPage) -> list[Book]:
        pass

    @abstractmethod
    async def save_book(self, book : Book) -> BookId:
        """Persist a new book and return its assigned ID."""
        pass

    @abstractmethod
    async def update_book(self, book : Book) -> None:
        pass

    @abstractmethod
    async def delete_book(self, book_id : BookId) -> None:
        pass
    

