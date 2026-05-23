from fastapi import APIRouter, Depends, HTTPException
from services.exports.di import get_book_service
from core.security import extract_user 
from services.book_service import BookService
from api.dtos.book_dto import SearchBookDto, RegisterBookDto
from api.dtos.loan_dto import LoanDto
from domain.user import User
from domain.book import Book
from core.exceptions import BookNotCreatedException
from core.validators import PositiveInt

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
async def registerBook(info : RegisterBookDto, user : User = Depends(extract_user), service : BookService = Depends(get_book_service)):
    try:
        id_created = await service.registerBook(info)
    except BookNotCreatedException as e:
        raise HTTPException(
            status_code= 409,
            detail=e.__str__()
        )
    
    return {
        "id" : id_created
    }

@router.post("/borrow/{id}")
async def borrowBook(loanDto : LoanDto, user : User = Depends(extract_user), bookService : BookService = Depends(get_book_service)):
    try:
        created_loan = await bookService.borrowBook(loanDto, user)
        return created_loan
    except:
        raise HTTPException(
            status_code=403,
            detail="Book cannot be borrowed"
        )
