from loans.application.loan_request_event_handler import LoanRequestEventHandler
from loans.domain.loan_request_status import LoanRequestStatus
from users.domain.user import User
from loans.domain.loan_request import LoanRequest
from books.domain.book_copy import BookCopy
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from shared.infrastructure.persistence.sql_unit_of_work import SQLUnitOfWork
from loans.infrastructure.adapters.sql_loan_req_repository import SQLLoanRequestRepository
from users.domain.user_notification import NotificationId, NotificationType, UserNotification
from users.infrastructure.adapters.sql_user_repository import SQLUserRepository

class SQLLoanRequestEventHandler(LoanRequestEventHandler):
    
    session_maker : async_sessionmaker[AsyncSession]

    def __init__(
            self,
            async_sessionmaker : async_sessionmaker[AsyncSession]
        ) -> None:
        super().__init__()
        self.session_maker = async_sessionmaker

    async def onCreateLoanRequest(self, user : User, loan : LoanRequest):
        #Do not do anything
        return
    
    
    async def onExpiredInterestTime(self, loan : LoanRequest):
        #A loan request expired: Delete it
        async with self.session_maker() as session:
            uow = SQLUnitOfWork(session)
            loan_req_repo = SQLLoanRequestRepository(session)
            user_repo = SQLUserRepository(session)
            async with uow:
                await loan_req_repo.remove_request(loan.loan_req_id)
                #And notify about it
                await user_repo.post_notification(
                    UserNotification(
                        NotificationId(0),
                        loan.user_id,
                        NotificationType.INTEREST_TIME_EXPIRED,
                        loan.loan_req_id
                    )
                )
        return

    async def onCopyAssigned(self, book_copy : BookCopy, loan : LoanRequest):
        #We need to handle the user notification here
        async with self.session_maker() as session:
            uow = SQLUnitOfWork(session)
            loan_req_repo = SQLLoanRequestRepository(session)
            user_repo = SQLUserRepository(session)
            async with uow:
                await user_repo.post_notification(UserNotification(
                    NotificationId(0),
                    loan.user_id,
                    NotificationType.REQ_ASSIGNED,
                    loan.loan_req_id
                ))
                loan.status = LoanRequestStatus.NOTIFICADA
                await loan_req_repo.update_loan_request(loan)
        return
        
    async def onPickupTimeExpired(self, loan : LoanRequest):
        #A loan request expired: Delete it
        async with self.session_maker() as session:
            uow = SQLUnitOfWork(session)
            loan_req_repo = SQLLoanRequestRepository(session)
            user_repo = SQLUserRepository(session)
            async with uow:
                await loan_req_repo.remove_request(loan.loan_req_id)
                #And notify about it
                await user_repo.post_notification(
                    UserNotification(
                        NotificationId(0),
                        loan.user_id,
                        NotificationType.PICKUP_TIME_EXPIRED,
                        loan.loan_req_id
                    )
                )
        return
