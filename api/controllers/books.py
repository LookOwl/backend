from fastapi import APIRouter, Depends, HTTPException
from services.exports.di import get_book_service
from core.security import extract_user 
from services.book_service import BookService
from api.dtos.book_dto import SearchBookDto, RegisterBookDto
from domain.user import User
from domain.book import Book
from core.exceptions import BookNotCreatedException

router = APIRouter(prefix="/books",tags=["books"])

@router.get("/")
async def getBooks(title:str | None = None,author:str | None= None,limit:int | None= None,offset:int | None= None, bookService : BookService = Depends(get_book_service) ):
    query_limit = limit + 1 if limit is not None else None
    result : list[Book] = await bookService.getBooks(SearchBookDto(
        title=title,
        author=author,
        limit=query_limit,
        offset=offset
    ))
    print(result)
    has_next = False
    next_cursor = None
    if limit is not None and len(result) > limit:
        has_next = True
        next_cursor = limit + offset if offset is not None else limit
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