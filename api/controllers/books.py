from fastapi import APIRouter, Depends
from api.services.exports.di import get_book_service 
from api.services.book_service import BookService
from api.dtos.book_dto import SearchBookDto
from domain.user import User
from domain.book import Book

router = APIRouter(prefix="/books",tags=["books"])

@router.get("/")
async def getBooks(params : SearchBookDto, bookService : BookService = Depends(get_book_service) ):
    result : list[Book] = await bookService.getBooks(params)
    has_next = False
    next_cursor = None
    if params.limit is not None and len(result) > params.limit:
        has_next = True
        next_cursor = params.limit + params.offset if params.offset is not None else params.limit  
    return {
        "data" : result,
        "page" : {
            "next_cursor" : { "offset" : next_cursor },
            "has_next" : has_next
        }
    }
