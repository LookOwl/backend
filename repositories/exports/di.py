from repositories.book_repository import BookRepository
from repositories.user_repository import UserRepository
from repositories.book_copy_repository import BookCopyRepository
from repositories.loan_repository import LoanRepository
from fastapi import Depends
from db.connection import get_db

def get_user_repository(
    db = Depends(get_db)
):
    return UserRepository(db)

def get_book_repository(
    db = Depends(get_db)
):
    return BookRepository(db)

def get_book_copy_repository(
    db = Depends(get_db)
):
    return BookCopyRepository(db)

def get_loan_repository(
    db = Depends(get_db)
):
    return LoanRepository(db)
