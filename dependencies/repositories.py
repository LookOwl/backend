from repositories.book_repository import BookRepository
from repositories.user_repository import UserRepository
from repositories.book_copy_repository import BookCopyRepository
from repositories.loan_repository import LoanRepository
from repositories.solicitud_libro_repository import SolicitudLibroRepository
from fastapi import Depends
from infrastructure.database.connection import async_get_db_session

def get_user_repository(
    db = Depends(async_get_db_session)
):
    return UserRepository(db)

def get_book_repository(
    db = Depends(async_get_db_session)
):
    return BookRepository(db)

def get_book_copy_repository(
    db = Depends(async_get_db_session)
):
    return BookCopyRepository(db)

def get_loan_repository(
    db = Depends(async_get_db_session)
):
    return LoanRepository(db)

def get_solicitud_libro_repository(
    db = Depends(async_get_db_session)
):
    return SolicitudLibroRepository(db)
