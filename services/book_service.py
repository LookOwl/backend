from domain.book import Book
from domain.user import User
from domain.enums.estado_prestamos import EstadoPrestamo
from api.dtos.book_dto import RegisterBookDto, SearchBookDto
from api.dtos.loan_dto import LoanDto
from uow.ApplicationUOW import AppUnitOfWork
from domain.loan import Loan
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from core.exceptions import BookNotCreatedException

from datetime import datetime, timezone

class BookService:
    def __init__(
            self, 
            uow : AppUnitOfWork
        ) -> None:
        self.uow = uow
        self.repo = uow.book_repo
        self.loan_repo = uow.loan_repo
        self.book_copy_repo = uow.solicitud_libro_repo

    async def getBooks(self,params : SearchBookDto) -> list[Book] :
        data = []
        
        if params.limit is not None and params.offset is not None:
            async with self.uow :
                data = await self.repo.get_books(
                    title=params.title,
                    author=params.author,
                    limit=params.limit,
                    offset=params.offset
                )
        elif params.limit is not None:
            async with self.uow:
                data = await self.repo.get_books(
                    title=params.title,
                    author=params.author,
                    limit=params.limit
                )
        else:
            async with self.uow:
                data = await self.repo.get_books(
                    title=params.title,
                    author=params.author
                )
            
        return data

    async def registerBook(self, book : RegisterBookDto) -> int | None:
        toCreate = Book(
            id=0,
            title=book.title,
            isbn=book.isbn,
            description=book.isbn,
            editorial=book.editorial,
            publication_date=book.publication_date,
            cover_url=book.cover_url.encoded_string(),
            language=book.language,
            author=book.author,
            category=book.category,
            page_count=book.page_count
        )
        try:
            async with self.uow:
                saved = await self.repo.save_book(toCreate)
            return saved.id
        except IntegrityError:
            raise BookNotCreatedException("ISBN already exists")
        except SQLAlchemyError:
            raise BookNotCreatedException("Unknown exception")
        
    async def borrowBook(self,loanDto:LoanDto, user : User):
        try:
            #El préstamo no puede exceder los 14 días
            if loanDto.n_days_requested > 14: raise IllegalBookLoan
            
            #El usuario debe tener menos de 3 préstamos activos
            active_loans = self.loan_repo.list(
                user_id = user.uid,
                status= EstadoPrestamo.ACTIVO,
                limit=4
            )
            if(len(active_loans) > 3): raise IllegalBookLoan
            
            # si se cumple todo, entonces insertémoslo en la cola
            
            self.loan_repo.create(Loan(
                user_id=int(user.uid),
                copy_code=loanDto.book_copy_id,
                status=EstadoPrestamo.PENDIENTE
            ))
        
        except Exception as e:
            raise e

class IllegalBookLoan(Exception): pass