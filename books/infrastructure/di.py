from fastapi import Depends
from books.application.use_cases.register_book import RegisterBook
from books.application.use_cases.search_books import SearchBook

from books.domain.book_repository import BookRepository
from shared.application.unit_of_work import UnitOfWork
from shared.infrastructure.persistence.di import get_sql_unit_of_work
from users.domain.user_repository import UserRepository
from users.infrastructure.di import get_sql_user_repo
from books.infrastructure.adapters.persistence.di import get_sql_book_repository

def get_search_book_uc(
    book_repo : BookRepository = Depends(get_sql_book_repository),
    uow : UnitOfWork = Depends(get_sql_unit_of_work)
):
    return SearchBook(
        book_repo,
        uow
    )

def get_register_book_uc(
    book_repository : BookRepository = Depends(get_sql_book_repository),
    user_repository : UserRepository = Depends(get_sql_user_repo),
    uow : UnitOfWork = Depends(get_sql_unit_of_work)
):
    return RegisterBook(
        book_repository,
        user_repository,
        uow
    )
