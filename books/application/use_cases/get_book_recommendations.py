from books.domain.book import Book, BookId
from books.domain.book_embedding_repository import BookEmbeddingRepository
from shared.application.unit_of_work import UnitOfWork


class GetBookRecommendations:
    """Use case: get book recommendations based on a reference book."""

    book_embedding_repo: BookEmbeddingRepository
    uow: UnitOfWork

    def __init__(
        self,
        book_embedding_repository: BookEmbeddingRepository,
        uow: UnitOfWork,
    ) -> None:
        self.book_embedding_repo = book_embedding_repository
        self.uow = uow

    async def execute(
        self, book_id: BookId, num_recommendations: int = 15
    ) -> list[Book]:
        async with self.uow:
            result: list[Book] = (
                await self.book_embedding_repo.get_recommendations_by_book(
                    book_id=book_id,
                    num_recommendations=num_recommendations,
                )
            )
        return result
