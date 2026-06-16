from fastapi import APIRouter, Depends, HTTPException

from books.application.use_cases.register_book import RegisterBook
from books.application.use_cases.search_books import SearchBook
from books.domain.book import Book
from books.infrastructure.http.dtos.register_book_dto import RegisterBookDto
from users.domain.user import User
from users.domain.user_role import UserRole

router = APIRouter(prefix="/books",tags=["books"])

@router.get("/")
async def getBooks(
    title:str | None = None,
    author:str | None= None,
    limit:int=20,
    offset:int = 0, 
    search_book : SearchBook = Depends()
):
    result : list[Book] = await search_book.execute(
        title=title,
        authors= [] if not author else [author]  ,
        limit=limit+1,
        offset=offset
    )

    has_next : bool= False

    if(len(result) > limit): has_next = True
    
    res : dict[str,list[Book]|dict[str,int|bool] ] = {
        "result" : result,
        "page" : {
            "offset" : offset,
            "limit" : limit,
            "has_next" : has_next
        }
    }

    return res

@router.post("/register")
async def registerBook(
    info : RegisterBookDto,
    user : User = Depends(), 
    register_book : RegisterBook = Depends()
):
    if user.role != UserRole.BIBLIOTECARIO:
        raise HTTPException(
            status_code=403,     #Forbidden
            detail="Sólo bibliotecarios autorizados"
        )
    try: 
        await register_book.execute(
            info.title,
            info.isbn,
            info.description,
            info.editorial,
            info.publication_date,
            info.cover_url.encoded_string(),
            info.language,
            info.author,
            info.category,
            info.page_count,
            user.id.uid
        )
    except Exception:
        raise HTTPException(
            status_code= 409,
            detail="No se pudo crear el libro"
        )
