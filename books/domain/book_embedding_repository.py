from abc import ABC, abstractmethod

from books.domain.book import Book, BookId


class BookEmbeddingRepository(ABC):
    """Port for accessing book embeddings and generating recommendations."""

    @abstractmethod
    async def get_recommendations_by_book(
        self, book_id: BookId, num_recommendations: int = 15
    ) -> list[Book]:
        """Return books similar to the given book based on embedding similarity."""
        pass

    @abstractmethod
    async def get_recommendations_by_query(
        self, query: str, num_recommendations: int = 15
    ) -> list[Book]:
        """Return books similar to the given text query based on embedding similarity."""
        pass
