from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loans.infrastructure.adapters.sql_loan_req_repository import SQLLoanRequestRepository
from loans.infrastructure.adapters.sql_loan_repository import SQLLoanRepository
from shared.infrastructure.persistence.di import get_async_sql_session


def get_sql_loan_repo(
    async_session : AsyncSession = Depends(get_async_sql_session)
):
    return SQLLoanRepository(
        async_session
    )

def get_sql_loan_req_repo(
        async_session : AsyncSession = Depends(get_async_sql_session)
):
    return SQLLoanRequestRepository(
        async_session
    )
