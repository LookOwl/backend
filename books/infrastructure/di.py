from fastapi import Depends
from books.application.use_cases.get_book_copies import GetBookCopies
from books.application.use_cases.get_book_recommendations import GetBookRecommendations
from books.application.use_cases.get_query_recommendations import GetQueryRecommendations
from books.application.use_cases.register_book import RegisterBook
from books.application.use_cases.register_book_copy import RegisterBookCopy
from books.application.use_cases.search_books import SearchBook

from books.application.use_cases.update_book_copy import UpdateBookCopy
from books.domain.book_copy_repository import BookCopyRepository
from books.domain.book_embedding_repository import BookEmbeddingRepository
from books.domain.book_repository import BookRepository
from shared.application.unit_of_work import UnitOfWork
from shared.infrastructure.persistence.di import get_sql_unit_of_work
from users.domain.user_repository import UserRepository
from users.infrastructure.di import get_sql_user_repo
from books.infrastructure.adapters.persistence.di import get_sql_book_copy_repository, get_sql_book_embedding_repository, get_sql_book_repository

def get_search_book_uc(
    book_repo : BookRepository = Depends(get_sql_book_repository),
    uow : UnitOfWork = Depends(get_sql_unit_of_work)
) -> SearchBook:
    return SearchBook(
        book_repo,
        uow
    )

def get_register_book_uc(
    book_repository : BookRepository = Depends(get_sql_book_repository),
    user_repository : UserRepository = Depends(get_sql_user_repo),
    book_embedding_repository : BookEmbeddingRepository = Depends(get_sql_book_embedding_repository),
    uow : UnitOfWork = Depends(get_sql_unit_of_work)
) -> RegisterBook:
    return RegisterBook(
        book_repository,
        user_repository,
        book_embedding_repository,
        uow
    )

def get_book_copies_uc(
    book_repository : BookRepository = Depends(get_sql_book_repository),
    user_repository : UserRepository = Depends(get_sql_user_repo),
    book_copy_repository : BookCopyRepository = Depends(get_sql_book_copy_repository),
    uow : UnitOfWork = Depends(get_sql_unit_of_work)
) -> GetBookCopies:
    return GetBookCopies(
        book_repository,
        book_copy_repository,
        uow
    )

def get_register_book_copies_uc(
    book_repository : BookRepository = Depends(get_sql_book_repository),
    user_repository : UserRepository = Depends(get_sql_user_repo),
    book_copy_repository : BookCopyRepository = Depends(get_sql_book_copy_repository),
    uow : UnitOfWork = Depends(get_sql_unit_of_work)
) -> RegisterBookCopy:
    return RegisterBookCopy(
        book_repository,
        user_repository,
        book_copy_repository,
        uow
    )

def get_updater_book_copies_uc(
    user_repository : UserRepository = Depends(get_sql_user_repo),
    book_copy_repository : BookCopyRepository = Depends(get_sql_book_copy_repository),
    uow : UnitOfWork = Depends(get_sql_unit_of_work)
) -> UpdateBookCopy:
    return UpdateBookCopy(
        user_repository,
        book_copy_repository,
        uow
    )

def get_book_recommendations_uc(
    book_embedding_repo: BookEmbeddingRepository = Depends(
        get_sql_book_embedding_repository
    ),
    uow: UnitOfWork = Depends(get_sql_unit_of_work)
) -> GetBookRecommendations:
    return GetBookRecommendations(
        book_embedding_repo,
        uow
    )

def get_query_recommendations_uc(
    book_embedding_repo: BookEmbeddingRepository = Depends(
        get_sql_book_embedding_repository
    ),
    uow: UnitOfWork = Depends(get_sql_unit_of_work)
) -> GetQueryRecommendations:
    return GetQueryRecommendations(
        book_embedding_repo,
        uow
    )
