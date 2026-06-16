from abc import ABC, abstractmethod
from books.domain.book import Book, BookId
from books.domain.book_search_criteria import BookSearchCriteria

class BookRepository(ABC):
    
    @abstractmethod
    async def get_by_id(self, book_id : BookId) -> Book:
        pass
    
    @abstractmethod
    async def find_similar_books(self, book : BookSearchCriteria) -> list[Book]:
        pass

    @abstractmethod
    async def save_book(self, book : Book) -> None:
        pass

    @abstractmethod
    async def update_book(self, book : Book) -> None:
        pass

    @abstractmethod
    async def delete_book(self, book_id : BookId) -> None:
        pass
    
    #TODO(Añadir dos metodos mas)
    #def get_similar(self, book : Book ) -> 

