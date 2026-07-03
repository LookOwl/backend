

from loans.application.loan_event_handler import LoanEventHandler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from loans.domain.loan import Loan
from loans.infrastructure.adapters.sql_loan_repository import SQLLoanRepository
from shared.infrastructure.persistence.sql_unit_of_work import SQLUnitOfWork

class SQLLoanEventHandler(LoanEventHandler):

    async_session_factory : async_sessionmaker[AsyncSession]

    def __init__(
            self,
            async_session_factory : async_sessionmaker[AsyncSession]
        ) -> None:
        super().__init__()
        self.async_session_factory = async_session_factory

    async def onLoanExpired(self, loan: Loan) -> None:
        async with self.async_session_factory() as session:
            #Update loan
            temp_loan = loan
            uow = SQLUnitOfWork(session)
            loan_repo = SQLLoanRepository(session)
            async with uow:
                temp_loan.expire()
                await loan_repo.update_loan(temp_loan)
        return
    
    async def onLoanReturned(self, loan: Loan) -> None:
        #Nothing to do (Possibly a notification, in the future?)
        return