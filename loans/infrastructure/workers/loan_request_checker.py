from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from loans.infrastructure.persistence.models.loan_request import SolicitudLibro
from loans.domain.loan_request_status import LoanRequestStatus
from loans.application.loan_request_dispatcher import LoanRequestEventDispatcher
from loans.domain.loan_request_event import LoanRequestInterestTimeExpired, LoanRequestPickupTimeExpired
from loans.domain.loan_request import LoanRequest, LoanRequestId, LoanRequestTimeRequested, LoanRequestWaitTime
from users.domain.user import UserId
from books.domain.book_copy import BookCopyId
from books.domain.book import BookId
class LoanRequestConsistencyVerifier:

    session : AsyncSession
    subject : LoanRequestEventDispatcher

    def __init__(
            self,
            async_session : AsyncSession,
            subject : LoanRequestEventDispatcher
        ) -> None:
        self.session = async_session
        self.subject = subject

    async def execute(
        self
    ):
        self.session.begin()
        #Find expired queue requests
        results1 = (
            await self.session.execute(
                select(SolicitudLibro)
                .where(SolicitudLibro.estado == LoanRequestStatus.PENDIENTE)
                .where(
                    SolicitudLibro.created_at + func.make_interval(0,0,0,0,SolicitudLibro.tiempo_espera,0,0) > func.now()
                )
            )
        ).scalars().all()
        #Find expired waiting requests 
        results2: Sequence[SolicitudLibro] = (
        await self.session.execute(
                select(SolicitudLibro)
                .where(SolicitudLibro.estado == LoanRequestStatus.NOTIFICADA)
                .where(
                    SolicitudLibro.created_at + func.make_interval(0,0,0,7,0,0,0,0) > func.now()
                )
            )
        ).scalars().all()
        await self.session.commit()

        # notify the first group
        for result in results1:
            await self.subject.notify(
                LoanRequestInterestTimeExpired(
                    LoanRequest(
                        LoanRequestId(result.id),
                    UserId(result.id_usuario),
                    BookId(result.id_libro),
                    BookCopyId(result.id_ejemplar) if result.id_ejemplar else None ,
                    LoanRequestWaitTime(result.tiempo_espera),
                    LoanRequestTimeRequested(result.tiempo_prestamo),
                    result.estado,
                    result.created_at,
                    result.updated_at
                    )
                )
            )
        #Notify the second group
        for result in results2:
            await self.subject.notify(
                LoanRequestPickupTimeExpired(
                    LoanRequest(
                        LoanRequestId(result.id),
                    UserId(result.id_usuario),
                    BookId(result.id_libro),
                    BookCopyId(result.id_ejemplar) if result.id_ejemplar else None ,
                    LoanRequestWaitTime(result.tiempo_espera),
                    LoanRequestTimeRequested(result.tiempo_prestamo),
                    result.estado,
                    result.created_at,
                    result.updated_at
                    )
                )
            )

            
