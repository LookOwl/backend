from abc import ABC, abstractmethod

from books.domain.book import BookId
from loans.domain.loan_request import LoanRequest, LoanRequestId

class LoanRequestRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id: LoanRequestId) -> LoanRequest | None:
        pass

    @abstractmethod
    async def get_by_book_id(self, id: BookId) -> list[LoanRequest]:
        pass

    @abstractmethod
    async def save_request(self, request: LoanRequest) -> None:
        pass
    
    @abstractmethod
    async def remove_request(self, id : LoanRequestId) -> None:
        pass

    @abstractmethod
    async def update_loan_request(self, loan_req : LoanRequest) -> None:
        pass