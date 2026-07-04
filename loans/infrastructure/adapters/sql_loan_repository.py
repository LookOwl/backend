
from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from books.domain.book import BookId
from books.domain.book_copy import BookCopyId, PhysicalBookCopyId
from books.infrastructure.persistence.models.book_copy import Ejemplar
from loans.domain.loan import LoanId, UserId
from loans.domain.loan_repo import LoanRepository
from loans.domain.loan_request import LoanRequestId
from sqlalchemy.ext.asyncio import AsyncSession
from loans.infrastructure.persistence.models.loan import Prestamo
from loans.domain.loan import Loan

class SQLLoanRepository(LoanRepository):
    async_session : AsyncSession

    def __init__(
            self,
            async_session : AsyncSession
    ) -> None:
        super().__init__()
        self.async_session = async_session

    
    async def get_by_id(self, id : LoanId) -> Loan | None:
        result = (
            await self.async_session.execute(
                select(Prestamo)
                .where(Prestamo.id == id.id)
                .options(
                    selectinload(Prestamo.ejemplar)
                )
            )
        ).scalar_one_or_none()
        if result is None: return None

        return self._to_domain(result)

    async def get_by_user(self, id: UserId) -> list[Loan]:
        results = (
            await self.async_session.execute(
                select(Prestamo)
                .where(Prestamo.id_usuario_asociado == id.uid)
                .options(
                    selectinload(Prestamo.ejemplar)
                )
            )
        ).scalars().all()

        return [ self._to_domain(result) for result in results ]
    
    async def get_by_book_id(self, id : BookId) -> list[Loan]:
        results = (
            await self.async_session.execute(
                select(Prestamo)
                .join(Prestamo.ejemplar)
                .where(Ejemplar.libro_id == id.id)
                .options(
                    selectinload(Prestamo.ejemplar)
                )
            )
        ).scalars().all()

        return [ self._to_domain(result) for result in results ]

    async def get_by_physical_book_id(self, id: PhysicalBookCopyId) -> Loan | None:
        result = (
            await self.async_session.execute(
                select(Prestamo)
                .join(Prestamo.ejemplar)
                .where(Ejemplar.codigo == id.physical_id)
                .options(
                    selectinload(Prestamo.ejemplar)
                )
            )
        ).scalar_one_or_none()
        if result is None : return None
        
        return self._to_domain(result)

    async def save_loan(self, loan : Loan) -> None:
        self.async_session.add(
            Prestamo(
                id_ejemplar = loan.book_copy_id.id,
                id_usuario_asociado = loan.user_id.uid,
                fecha_aprobacion = loan.approval_date,
                fecha_vencimiento = loan.due_date,
                fecha_regreso = loan.return_date,
                estado = loan.status,
                solicitud_id = loan.loan_request_id.id
            )
        )
        await self.async_session.flush()
        return

    
    async def update_loan(self, loan: Loan) -> None:
        (
            await self.async_session.execute(
                update(Prestamo)
                .where(Prestamo.id == loan.id.id)
                .values(
                    id_ejemplar = loan.book_copy_id.id,
                    id_usuario_asociado = loan.user_id.uid,
                    fecha_aprobacion = loan.approval_date,
                    fecha_vencimiento = loan.due_date,
                    fecha_regreso = loan.return_date,
                    estado = loan.status
                )
            )
        )
        await self.async_session.flush()
        return

    
    async def delete_loan(self, id : LoanId) -> None:
        await self.async_session.execute(
            delete(Prestamo)
            .where(Prestamo.id == id.id)
        )
        await self.async_session.flush()

    def _to_domain(self, prestamo : Prestamo) -> Loan:
        return Loan(
            LoanId(prestamo.id),
            UserId(prestamo.id_usuario_asociado),
            BookCopyId(prestamo.id_ejemplar),
            BookId(prestamo.ejemplar.libro_id),
            prestamo.fecha_aprobacion,
            prestamo.fecha_vencimiento,
            prestamo.fecha_regreso,
            prestamo.estado,
            LoanRequestId(prestamo.solicitud_id)
        )