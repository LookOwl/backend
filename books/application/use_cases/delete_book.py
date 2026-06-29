from books.domain.book import BookId
from books.domain.book_copy_repository import BookCopyRepository
from books.domain.book_repository import BookRepository
from shared.application.unit_of_work import UnitOfWork
from users.domain.user import User
from users.domain.user_id import UserId
from users.domain.user_repository import UserRepository


class DeleteBook:

    def __init__(
        self,
        user_repository: UserRepository,
        book_repository: BookRepository,
        book_copy_repository: BookCopyRepository,
        uow: UnitOfWork
    ) -> None:
        self.user_repository = user_repository
        self.book_repository = book_repository
        self.book_copy_repository = book_copy_repository
        self.uow = uow

    async def execute(
        self,
        book_id: int,
        user_id: int
    ):
        async with self.uow:
            user: User | None = await self.user_repository.get_by_id(UserId(uid=user_id))
            if not user:
                raise Exception("Usuario no encontrado")

            book = await self.book_repository.get_by_id(BookId(id=book_id))
            if not book:
                raise Exception("Libro no existente o ya borrado")

            loaned_copies = await self.book_copy_repository.count_loaned_copies_per_book(BookId(id=book_id))
            if loaned_copies > 0:
                raise Exception(
                    "No se puede borrar el libro porque tiene ejemplares actualmente en préstamo"
                )

            await self.book_repository.delete_book(BookId(id=book_id))
