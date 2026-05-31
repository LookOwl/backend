from repositories.book_repository import BookRepository
from repositories.user_repository import UserRepository
from repositories.book_copy_repository import BookCopyRepository
from repositories.loan_repository import LoanRepository
from repositories.solicitud_libro_repository import SolicitudLibroRepository
from repositories.book_embedding_repository import BookEmbeddingRepository
from fastapi import Depends
from dependencies.infrastructure import async_get_db_session

#Ya no creo que estos sean necesarios

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

def get_book_embedding_repository(
    db = Depends(get_db)
):
    return BookEmbeddingRepository(db)
