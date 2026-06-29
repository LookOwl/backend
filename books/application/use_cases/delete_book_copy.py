from books.domain.book_copy import BookCopyId
from books.domain.book_copy_repository import BookCopyRepository
from shared.application.unit_of_work import UnitOfWork
from users.domain.user import User
from users.domain.user_id import UserId
from users.domain.user_repository import UserRepository


class DeleteBookCopy:
    def __init__(
        self,
        user_repository: UserRepository,
        book_copy_repository: BookCopyRepository,
        uow: UnitOfWork
    ) -> None:
        self.user_repository = user_repository
        self.book_copy_repository = book_copy_repository
        self.uow = uow

    async def execute(
        self,
        copy_id: str,
        user_id: int
    ):
        async with self.uow:
            user : User | None = await self.user_repository.get_by_id(UserId(uid = user_id))
            if not user:
                raise Exception("User not found")

            deleted = await self.book_copy_repository.delete_book_copy(BookCopyId(physical_id=copy_id))

            if not deleted:
                raise Exception("Element already deleted or never existed")
