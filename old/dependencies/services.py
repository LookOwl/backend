from fastapi import Depends
from old.services.auth_service import AuthService
from old.services.book_service import BookService
from old.dependencies.uow import get_unit_of_work
from old.services.borrowing_service import BorrowingService
from old.services.loan_service import LoanService
from old.dependencies.orchestrator import get_borrowing_orchestrator

def get_auth_service(
    uow = Depends(get_unit_of_work)
):
    return AuthService(uow)

def get_book_service(
    uow = Depends(get_unit_of_work)
):
    return BookService(uow)

def get_loan_service(
    uow = Depends(get_unit_of_work)

):
    return LoanService(uow)

def get_borrowing_service(
    orch = Depends(get_borrowing_orchestrator)
):
    return BorrowingService(orch)

    