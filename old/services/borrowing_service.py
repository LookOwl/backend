from old.domain.solicitud_libro import BookRequest, EstadoSolicitud, datetime
from old.orchestrator.borrowing_orchestrator import BorrowingOrchestrator, User
from old.api.dtos.loan_dto import LoanDto

class BorrowingService:
    def __init__(
            self,
            orchestrator : BorrowingOrchestrator
    ):
        self.orchestrator = orchestrator

    #Caso usuario quiere solicitar el préstamo de un libro
    async def create_loan_request(self,request_dto : LoanDto, user: User):
        try:
            request = BookRequest(
                id = None,
                user_id= user.uid,
                book_id=request_dto.book_id,
                copy_code = "",
                wait_time = request_dto.interest_window,
                loan_time = request_dto.n_days_requested,
                status = EstadoSolicitud.PENDIENTE,
                created_at = datetime.now(),
                updated_at = datetime.now()
            )
            await self.orchestrator.submit_loan_request(
                user = user,
                req = request
            )
        except Exception as e:
            raise UnprocessableRequestException(str(e))
    
    #Caso bibliotecario quiere ver la cola privilegiada de un libro
    async def get_priviledged_requests(self, book_id : int):
        try:
            requests = await self.orchestrator.get_priviledged_queue(book_id)
            return requests
        except Exception as e:
            raise UnprocessableRequestException(str(e))

    
      
class UnprocessableRequestException(Exception) : pass