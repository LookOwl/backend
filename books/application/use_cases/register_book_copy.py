from books.domain.book import Book, BookId
from books.domain.book_copy import BookCopy, BookCopyId, BookCopyStatus
from books.domain.book_copy_repository import BookCopyRepository
from books.domain.book_repository import BookRepository
from shared.application.unit_of_work import UnitOfWork
from users.domain.user import User
from users.domain.user_id import UserId
from users.domain.user_repository import UserRepository


class RegisterBookCopy:

    def __init__(
        self,
        book_repository : BookRepository,
        user_repository : UserRepository,
        book_copy_repository : BookCopyRepository,
        uow : UnitOfWork
    ) -> None:
        self.book_repo = book_repository
        self.user_repo = user_repository
        self.book_copy_repository = book_copy_repository
        self.uow = uow

    async def execute(
        self,
        copy_id: str,
        book_id: int,
        user_id : int
    ):
        async with self.uow:
            user : User | None = await self.user_repo.get_by_id(UserId(uid = user_id))

            if not user:
                raise Exception("User not found")

            book: Book | None = await self.book_repo.get_by_id(BookId(id=book_id))

            if not book:
                raise Exception("Book not found")

            book_copy : BookCopy = BookCopy(
                copy_id=BookCopyId(copy_id),
                book_id=BookId(book_id),
                status=BookCopyStatus.DISPONIBLE
            )

            await self.book_copy_repository.save_book_copy(book_copy)
