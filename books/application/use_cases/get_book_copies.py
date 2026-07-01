from books.domain.book import Book, BookId
from books.domain.book_copy_repository import BookCopyRepository
from books.domain.book_repository import BookRepository
from shared.application.unit_of_work import UnitOfWork


class GetBookCopies:

    def __init__(
        self,
        book_repository: BookRepository,
        book_copy_repository: BookCopyRepository,
        uow: UnitOfWork,
    ) -> None:
        self.book_repository = book_repository
        self.book_copy_repository = book_copy_repository
        self.uow = uow

    async def execute(
        self,
        book_id: int,
    ):
        async with self.uow:
            book : Book | None = await self.book_repository.get_by_id(BookId(id=book_id))
            if not book:
                raise Exception("Book copy not found")

            result = await self.book_copy_repository.find_by_book(BookId(id=book_id))

        return result
