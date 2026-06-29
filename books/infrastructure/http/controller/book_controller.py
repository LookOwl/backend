from fastapi import APIRouter, Depends, HTTPException, Query
from books.application.use_cases.delete_book import DeleteBook
from books.application.use_cases.get_book_copies import GetBookCopies
from books.application.use_cases.register_book import RegisterBook
from books.application.use_cases.register_book_copy import RegisterBookCopy
from books.application.use_cases.search_books import SearchBook
from books.domain.book import Book, BookId
from books.domain.book_copy import BookCopy
from books.infrastructure.di import get_book_copies_uc, get_deleter_book_uc, get_register_book_copies_uc, get_register_book_uc, get_search_book_uc
from books.infrastructure.http.dtos.book_copy_dto import BookCopyDto
from books.infrastructure.http.dtos.book_dto import BookDto
from books.infrastructure.http.dtos.register_book_copy_dto import RegisterBookCopyDto
from books.infrastructure.http.dtos.register_book_dto import RegisterBookDto
from books.application.use_cases.get_book_recommendations import GetBookRecommendations
from books.infrastructure.di import get_book_recommendations_uc
from shared.infrastructure.di import jwt_auth_guard
from users.domain.user import User
from users.domain.user_role import UserRole

router = APIRouter(prefix="/books",tags=["books"])

@router.get("/")
async def get_books(
    title:str | None = None,
    author:str | None= None,
    limit:int=20,
    offset:int = 0,
    search_book : SearchBook = Depends(get_search_book_uc)
):
    results : list[Book] = await search_book.execute(
        title=title,
        authors= [] if not author else [author]  ,
        limit=limit+1,
        offset=offset
    )

    has_next : bool= False

    if len(results) > limit:
        has_next = True

    res : dict[str,list[BookDto]|dict[str,int|bool] ] = {
        "result" : [ BookDto.to_dto(result) for result in results ],
        "page" : {
            "offset" : offset,
            "limit" : limit,
            "has_next" : has_next
        }
    }

    return res

@router.post("/register")
async def register_book(
    info : RegisterBookDto,
    user : User = Depends(jwt_auth_guard),
    register_book : RegisterBook = Depends(get_register_book_uc)
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

@router.get("/{book_id}/copies", tags=["book-copies"])
async def get_copies(
    book_id: int,
    get_copies: GetBookCopies = Depends(get_book_copies_uc)
):
    try:
        results: list[BookCopy] = await get_copies.execute(book_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return {"copies" : [BookCopyDto.to_dto(result) for result in results]}

@router.post("/{book_id}/copies", tags=["book-copies"])
async def register_book_copy(
    book_id: int,
    info: RegisterBookCopyDto,
    user: User = Depends(jwt_auth_guard),
    register_book_copy: RegisterBookCopy = Depends(get_register_book_copies_uc)
):
    if user.role != UserRole.BIBLIOTECARIO:
        raise HTTPException(
            status_code=403,     #Forbidden
            detail="Sólo bibliotecarios autorizados"
        )
    try:
        await register_book_copy.execute(
            info.copy_id,
            book_id,
            user.id.uid
        )
    except Exception as exc:
        raise HTTPException(
            status_code=409,
            detail=f"No se pudo crear la copia de libro, {exc}"
        )

@router.get("/{book_id}/recommendations", tags=["recommendations"])
async def recommend_by_book(
    book_id: int,
    limit: int = Query(default=15, ge=1, le=50),
    get_recommendations: GetBookRecommendations = Depends(
        get_book_recommendations_uc
    ),
):
    try:
        books = await get_recommendations.execute(
            book_id=BookId(book_id),
            num_recommendations=limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"recommendations": [BookDto.to_dto(b) for b in books]}

@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    user: User = Depends(jwt_auth_guard),
    delete_book: DeleteBook = Depends(get_deleter_book_uc)
):
    if user.role != UserRole.BIBLIOTECARIO:
        raise HTTPException(
            status_code=403,
            detail="Solo bibliotecarios autorizados"
        )

    try:
        await delete_book.execute(
            book_id,
            user.id.uid
        )
    except Exception as exc:
        raise HTTPException(
            status_code=409,
            detail=f"No se pudo eliminar el libro, {exc}"
        )
