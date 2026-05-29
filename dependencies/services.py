from fastapi import Depends
from services.auth_service import AuthService
from services.book_service import BookService
from services.loan_service import LoanService
from dependencies.repositories import get_user_repository
from dependencies.repositories import get_book_repository
from dependencies.repositories import get_loan_repository

def get_auth_service(
    user_repo = Depends(get_user_repository)
):
    return AuthService(user_repo)

def get_book_service(
        book_repo = Depends(get_book_repository)
):
    return BookService(book_repo)

def get_loan_service(
    loan_repo = Depends(get_loan_repository)
):
    return LoanService(
        loan_repo=loan_repo
    )