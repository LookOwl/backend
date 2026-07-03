from books.domain.book import Book, BookId
from books.domain.book_repository import BookRepository
from shared.application.unit_of_work import UnitOfWork


class GetBookById:

    def __init__(
            self,
            book_repository : BookRepository,
            uow : UnitOfWork
        ) -> None:
        self.book_repo = book_repository
        self.uow = uow

    async def execute(
        self,
        id: int
    ) -> Book:
        async with self.uow:
            book : Book | None = await self.book_repo.get_by_id(BookId(id=id))
            if not book:
                raise Exception("Book not found")
        return book
