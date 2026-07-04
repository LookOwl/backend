from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from books.domain.book import BookId
from books.domain.book_copy import BookCopyId
from loans.application.loan_dispatcher import LoanEventDispatcher
from sqlalchemy.ext.asyncio import AsyncSession

from loans.domain.loan import Loan, LoanId
from loans.domain.loan_events import LoanExpired
from loans.domain.loan_status import LoanStatus
from loans.infrastructure.persistence.models.loan import Prestamo
from users.domain.user_id import UserId

class LoanConsistencyVerifier:

    loan_event_dispatcher : LoanEventDispatcher
    session : AsyncSession

    def __init__(
            self,
            session : AsyncSession,
            loan_event_dispatcher : LoanEventDispatcher
        ) -> None:
        self.loan_event_dispatcher = loan_event_dispatcher
        self.session = session

    async def execute(self):
        self.session.begin()
        expired_loans = (
            await self.session.execute(
                select(Prestamo)
                .where(Prestamo.estado == LoanStatus.ACTIVO)
                .where(Prestamo.fecha_vencimiento < func.now())
                .options(
                    selectinload(Prestamo.ejemplar)
                )
            )
        ).scalars().all()
        await self.session.commit()

        for loan in expired_loans:
            await self.loan_event_dispatcher.notify(
                LoanExpired(
                    Loan(
                        LoanId(loan.id),
                        UserId(loan.id_usuario_asociado),
                        BookCopyId(loan.id_ejemplar),
                        BookId(loan.ejemplar.libro_id),
                        loan.fecha_aprobacion,
                        loan.fecha_vencimiento,
                        loan.fecha_regreso,
                        loan.estado
                    )
                )
            )