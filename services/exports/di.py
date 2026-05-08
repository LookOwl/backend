from fastapi import Depends
from services.auth_service import AuthService
from services.book_service import BookService
from repositories.exports.di import get_user_repository
from repositories.exports.di import get_book_repository

def get_auth_service(
    user_repo = Depends(get_user_repository)
):
    return AuthService(user_repo)

def get_book_service(
        book_repo = Depends(get_book_repository)
):
    return BookService(book_repo)