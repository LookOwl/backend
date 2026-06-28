from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from books.infrastructure.adapters.persistence.sql_book_embedding_repository import SQLBookEmbeddingRepository
from books.infrastructure.adapters.persistence.sql_book_copy_repository import SQLBookCopyRepository
from shared.infrastructure.persistence.di import get_async_sql_session
from books.infrastructure.adapters.persistence.sql_book_repository import SQLBookRepository

def get_sql_book_repository(
    session : AsyncSession = Depends(get_async_sql_session)
):
    return SQLBookRepository(
        session
    )

def get_sql_book_copy_repository(
    session : AsyncSession = Depends(get_async_sql_session)
):
    return SQLBookCopyRepository(
        session
    )

def get_sql_book_embedding_repository(
    session: AsyncSession = Depends(get_async_sql_session)
):
    return SQLBookEmbeddingRepository(
        session
    )
