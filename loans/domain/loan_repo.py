from abc import ABC, abstractmethod

from books.domain.book import BookId
from books.domain.book_copy import PhysicalBookCopyId
from loans.domain.loan import LoanId
from loans.domain.loan import Loan
from users.domain.user_id import UserId


class LoanRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id : LoanId) -> Loan | None:
        pass

    @abstractmethod
    async def get_by_user(self, id : UserId) -> list[Loan]:
        pass

    @abstractmethod
    async def get_by_book_id(self, id : BookId) -> list[Loan]:
        pass

    @abstractmethod
    async def get_by_physical_book_id(self, id : PhysicalBookCopyId) -> Loan | None:
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