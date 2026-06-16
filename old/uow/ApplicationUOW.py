from old.repositories.book_copy_repository import BookCopyRepository
from old.repositories.book_repository import BookRepository
from old.repositories.loan_repository import LoanRepository
from old.repositories.solicitud_libro_repository import SolicitudLibroRepository
from old.repositories.user_repository import UserRepository
from old.repositories.book_copy_repository import BookCopyRepository
from old.repositories.book_embedding_repository import BookEmbeddingRepository

from sqlalchemy.ext.asyncio import AsyncSession

class AppUnitOfWork:
    _session : AsyncSession
    book_repo : BookRepository
    loan_repo : LoanRepository
    solicitud_libro_repo : SolicitudLibroRepository
    user_repo : UserRepository
    book_copy_repo : BookCopyRepository
    book_embedd_repo : BookEmbeddingRepository     
    
    def __init__(
            self,
            session : AsyncSession
        ):
        # registrar todos los repos
        self._session = session
        self.book_repo = BookRepository(session)
        self.loan_repo = LoanRepository(session)
        self.solicitud_libro_repo = SolicitudLibroRepository(session)
        self.user_repo = UserRepository(session)
        self.book_copy_repo = BookCopyRepository(session)
        self.book_embedd_repo = BookEmbeddingRepository(session)    
    
    
    #Estas funciones son para el uso de la clase con las
    #cláusulas `async with`
    async def __aenter__(self):
        await self._session.begin()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            try:
                await self._session.commit()
            except Exception as e:
                try: 
                    await self._session.rollback()
                except Exception as rollback_failure:
                    raise RollbackException() from rollback_failure
                raise CommitException() from e
        else:
            try:
                await self._session.rollback()
            except Exception as rollback_failure:
                raise RollbackException() from rollback_failure
        return False
    

class RollbackException(Exception) : pass
class CommitException(Exception) : pass