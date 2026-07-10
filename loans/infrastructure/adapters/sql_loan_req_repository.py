from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from books.domain.book import BookId
from books.domain.book_copy import BookCopyId
from users.domain.user import UserId
from loans.domain.loan_request import LoanRequest, LoanRequestId, LoanRequestStatus, LoanRequestTimeRequested, LoanRequestWaitTime
from loans.domain.loan_request_repo import LoanRequestRepository
from loans.infrastructure.persistence.models.loan_request import SolicitudLibro


class SQLLoanRequestRepository(LoanRequestRepository):
    
    async_session : AsyncSession
    
    def __init__(
        self,
        async_session : AsyncSession
    ) -> None:
        self.async_session = async_session

    
    async def get_by_id(self, id: LoanRequestId) -> LoanRequest | None:
        result = (
            await self.async_session.execute(
            select(SolicitudLibro)
            .where(SolicitudLibro.id == id.id)
        )).scalar_one_or_none()
        if result is None: return None
        return self._to_domain(result)

    async def get_by_copy_id(self, id: BookCopyId) -> LoanRequest | None:
        # A copy is hard-locked to at most one request awaiting pickup (NOTIFICADA)
        # at a time. Older requests that were fulfilled (COMPLETADA) or expired
        # (CANCELADA) keep their id_ejemplar, so we must scope by status. Ordering
        # newest-first + limit 1 stays safe against any legacy NOTIFICADA duplicates
        # left by data created before the COMPLETADA lifecycle existed.
        result = (
            await self.async_session.execute(
            select(SolicitudLibro)
            .where(
                SolicitudLibro.id_ejemplar == id.id,
                SolicitudLibro.estado == LoanRequestStatus.NOTIFICADA,
            )
            .order_by(SolicitudLibro.created_at.desc())
            .limit(1)
        )).scalars().first()
        if result is None: return None
        return self._to_domain(result)

    async def get_n_first_pending_by_book_id(self, id: BookId, limit : int) -> list[LoanRequest]:
        results = (
            await self.async_session.execute(
                select(SolicitudLibro)
                .where(SolicitudLibro.id_libro == id.id)
                .where(SolicitudLibro.estado == LoanRequestStatus.PENDIENTE)
                .order_by(SolicitudLibro.created_at)
                .limit(limit)
            )
        ).scalars()
        
        return [
            self._to_domain(result) for result in results
        ]

    async def count_pending_by_book_id(self, id: BookId) -> int:
        results = (
            await self.async_session.execute(
                select(func.count())
                .select_from(SolicitudLibro)
                .where(SolicitudLibro.id_libro == id.id)
                .where(SolicitudLibro.estado == LoanRequestStatus.PENDIENTE)
            )
        ).scalar_one()
        
        return results

    async def save_request(self, request: LoanRequest) -> None:
        self.async_session.add(
            SolicitudLibro(
                id_usuario = request.user_id.uid,
                id_libro = request.book_id.id,
                id_ejemplar = request.book_copy_code.id if request.book_copy_code else None,
                tiempo_espera= request.wait_time.time,
                tiempo_prestamo = request.loan_time.time,
                estado = request.status 
            )
        )
        await self.async_session.flush()
        return
    
    
    async def remove_request(self, id : LoanRequestId) -> None:
        await self.async_session.execute(
            update(SolicitudLibro)
            .where(SolicitudLibro.id == id.id)
            .values(
                estado = LoanRequestStatus.CANCELADA,
                updated_at = func.now()
            )
        )
        await self.async_session.flush()
        return

    
    async def update_loan_request(self, loan_req : LoanRequest) -> None:
        await self.async_session.execute(
            update(SolicitudLibro)
            .where(SolicitudLibro.id == loan_req.loan_req_id.id)
            .values(
                id_usuario = loan_req.user_id.uid,
                id_libro = loan_req.book_id.id,
                id_ejemplar = loan_req.book_copy_code.id if loan_req.book_copy_code else None,
                tiempo_espera= loan_req.wait_time.time,
                tiempo_prestamo = loan_req.loan_time.time,
                estado = loan_req.status,
                updated_at = func.now()
            )
        )
        await self.async_session.flush()
        return
    
    def _to_domain(self,solicitud : SolicitudLibro) -> LoanRequest:
        return LoanRequest(
            LoanRequestId(solicitud.id),
            UserId(solicitud.id_usuario),
            BookId(solicitud.id_libro),
            BookCopyId(solicitud.id_ejemplar) if solicitud.id_ejemplar else None ,
            LoanRequestWaitTime(solicitud.tiempo_espera),
            LoanRequestTimeRequested(solicitud.tiempo_prestamo),
            solicitud.estado,
            solicitud.created_at,
            solicitud.updated_at
        )