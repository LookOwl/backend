from sqlalchemy import delete, func, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from books.domain.book import BookId
from books.domain.book_copy import BookCopy, BookCopyId
from books.domain.book_copy_repository import BookCopyRepository
from books.infrastructure.persistence.models.book_copy import Ejemplar


class SQLBookCopyRepository(BookCopyRepository):
    async_session : AsyncSession
    def __init__(
            self,
            async_session : AsyncSession
    ) -> None:
        super().__init__()
        self.async_session = async_session

    async def get_by_id(self, copy_id : BookCopyId) -> BookCopy | None:
        result = (
            await self
                .async_session
                .execute(
                    select(Ejemplar)
                    .where(Ejemplar.codigo == copy_id.physical_id )
                )
            ).scalar_one_or_none()
        if not result:
            return None
        return self._to_domain(result)

    async def count_available_copies_per_book(self, book_id : BookId) -> int:
        return (
            await self.async_session.execute(
                select(func.count())
                .select_from(Ejemplar).where(Ejemplar.libro_id == book_id.id)
            )
        ).scalar_one()

    async def find_by_book(self, id : BookId) -> list[BookCopy]:
        results = (
            await self
                .async_session
                .execute(
                    select(Ejemplar)
                    .where(Ejemplar.libro_id == id.id )
                )
            ).scalars()
        return [
            self._to_domain(result) for result in results
        ]


    async def save_book_copy(self, book_copy : BookCopy) -> None:
        self.async_session.add(
            Ejemplar(
                codigo = book_copy.copy_id.physical_id,
                libro_id = book_copy.book_id.id,
                estado = book_copy.status
            )
        )
        await self.async_session.flush()
        return

    async def update_book_copy(self, book_copy : BookCopy) -> None:
        (
            await self.async_session.execute(
                update(Ejemplar)
                .where(Ejemplar.codigo == book_copy.copy_id.physical_id)
                .values(
                    codigo = book_copy.copy_id.physical_id,
                    libro_id = book_copy.book_id.id,
                    estado = book_copy.status
                )
            )
        )
        await self.async_session.flush()
        return


    async def delete_book_copy(self, book_copy : BookCopyId) -> None:
        (
            await self.async_session.execute(
                delete(Ejemplar)
                .where(Ejemplar.codigo == book_copy.physical_id)
            )
        )
        await self.async_session.flush()
        return

    def _to_domain(self, ejemplar: Ejemplar) -> BookCopy:
        return BookCopy(
            BookCopyId(ejemplar.codigo),
            BookId(ejemplar.libro_id),
            ejemplar.estado
        )
