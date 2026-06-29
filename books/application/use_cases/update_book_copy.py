from books.domain.book_copy import BookCopy, BookCopyId, BookCopyStatus
from books.domain.book_copy_repository import BookCopyRepository
from shared.application.unit_of_work import UnitOfWork
from users.domain.user import User
from users.domain.user_id import UserId
from users.domain.user_repository import UserRepository


class UpdateBookCopy:

    def __init__(
        self,
        user_repository : UserRepository,
        book_copy_repository : BookCopyRepository,
        uow : UnitOfWork
    ) -> None:
        self.user_repo = user_repository
        self.book_copy_repository = book_copy_repository
        self.uow = uow

    async def execute(
        self,
        copy_id: str,
        user_id: int,
        status: BookCopyStatus
    ):
        async with self.uow:
            user : User | None = await self.user_repo.get_by_id(UserId(uid = user_id))
            if not user:
                raise Exception("User not found")

            book_copy : BookCopy | None = await self.book_copy_repository.get_by_id(BookCopyId(physical_id=copy_id))
            if not book_copy:
                raise Exception("Book copy not found")

            book_copy.status = status

            await self.book_copy_repository.update_book_copy(book_copy)
