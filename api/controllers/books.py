from fastapi import APIRouter, Depends, HTTPException
from core.auth_guard import user_auth_guard
from dependencies.services import get_book_service, get_borrowing_service
from services.book_service import BookService
from api.dtos.book_dto import SearchBookDto, RegisterBookDto
from api.dtos.loan_dto import LoanDto
from domain.user import User, RolUsuario
from domain.book import Book
from core.exceptions import BookNotCreatedException
from core.validators import PositiveInt
from services.borrowing_service import BorrowingService

router = APIRouter(prefix="/books",tags=["books"])

@router.get("/")
async def getBooks(title:str | None = None,author:str | None= None,limit:int=20,offset:int = 0, bookService : BookService = Depends(get_book_service) ):
    query_limit = limit + 1
    result : list[Book] = await bookService.getBooks(SearchBookDto(
        title=title,
        author=author,
        limit=query_limit,
        offset=offset
    ))
    
    has_next = False
    next_cursor = None
    if len(result) > limit:
        has_next = True
        next_cursor = limit + offset
        result.pop(-1)  
    return {
        "data" : result,
        "page" : {
            "next_cursor" : { "offset" : next_cursor },
            "has_next" : has_next
        }
    }

@router.post("/register")
async def registerBook(info : RegisterBookDto, user : User = Depends(user_auth_guard), service : BookService = Depends(get_book_service)):
    if user.role != RolUsuario.BIBLIOTECARIO:
        raise HTTPException(
            status_code=403,     #Forbidden
            detail="Sólo bibliotecarios autorizados"
        )
    try: 
        id_created = await service.registerBook(info)
        return {
            "id" : id_created
        }
    except BookNotCreatedException as e:
        raise HTTPException(
            status_code= 409,
            detail="No se pudo crear el libro"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error fatal: {}".format(e.__str__())    #TODO(Retirar esto en produccion)
        )

@router.post("/borrow/{id}")
async def borrowBook(loanDto : LoanDto, user : User = Depends(user_auth_guard), borrowService : BorrowingService = Depends(get_borrowing_service)):
    try:
        await borrowService.create_loan_request(loanDto, user)
        
        return {
            "result" : "ok"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=f"Book cannot be borrowed: {e}"
        )
