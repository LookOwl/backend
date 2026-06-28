from abc import ABC, abstractmethod

from loans.domain.loan import LoanId
from loans.domain.loan import Loan


class LoanRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id : LoanId) -> Loan | None:
        pass

    @abstractmethod
    async def save_loan(self, loan : Loan) -> None:
        pass

    @abstractmethod
    async def update_loan(self, loan: Loan) -> None:
        pass

    @abstractmethod
    async def delete_loan(self, id : LoanId) -> None:
        pass