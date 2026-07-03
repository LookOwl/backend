from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from books.domain.book import BookId
from books.domain.book_copy import PhysicalBookCopyId
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
                codigo_ejemplar = request.book_copy_code.physical_id if request.book_copy_code else None,
                tiempo_espera= request.wait_time.time,
                tiempo_prestamo = request.loan_time.time,
                estado = request.status 
            )
        )
        await self.async_session.flush()
        return
    
    
    async def remove_request(self, id : LoanRequestId) -> None:
        await self.async_session.execute(
            delete(SolicitudLibro)
            .where(SolicitudLibro.id == id.id)
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
                codigo_ejemplar = loan_req.book_copy_code.physical_id if loan_req.book_copy_code else None,
                tiempo_espera= loan_req.wait_time.time,
                tiempo_prestamo = loan_req.loan_time.time,
                estado = loan_req.status
            )
        )
        await self.async_session.flush()
        return
    
    def _to_domain(self,solicitud : SolicitudLibro) -> LoanRequest:
        return LoanRequest(
            LoanRequestId(solicitud.id),
            UserId(solicitud.id_usuario),
            BookId(solicitud.id_libro),
            PhysicalBookCopyId(solicitud.codigo_ejemplar) if solicitud.codigo_ejemplar else None ,
            LoanRequestWaitTime(solicitud.tiempo_espera),
            LoanRequestTimeRequested(solicitud.tiempo_prestamo),
            solicitud.estado,
            solicitud.created_at,
            solicitud.updated_at
        )