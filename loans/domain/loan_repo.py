from abc import ABC, abstractmethod

from loans.domain.loan import LoanId
from old.domain.loan import Loan


class LoanRepository(ABC):

    @abstractmethod
    def get_by_id(self, id : LoanId) -> Loan:
        pass

    @abstractmethod
    def save_loan(self, loan : Loan) -> None:
        pass

    @abstractmethod
    def update_loan(self, loan: Loan) -> None:
        pass

    @abstractmethod
    def delete_loan(self, id : LoanId) -> None:
        pass