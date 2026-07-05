from fastapi import APIRouter, Depends, HTTPException, Query
from books.application.use_cases.delete_book import DeleteBook
from books.application.use_cases.get_book_by_id import GetBookById
from books.application.use_cases.get_book_copies import GetBookCopies
from books.application.use_cases.register_book import RegisterBook
from books.application.use_cases.register_book_copy import RegisterBookCopy
from books.application.use_cases.search_books import AdvancedSearchBooks, SearchBooks
from books.application.use_cases.update_book import UpdateBook
from books.domain.book import Book, BookId
from books.domain.book_copy import BookCopy
from books.infrastructure.di import get_advanced_search_book_uc, get_book_copies_uc, get_deleter_book_uc, get_register_book_copies_uc, get_register_book_uc, get_search_book_by_id_uc, get_search_book_uc, get_updater_book_uc
from books.infrastructure.http.dtos.book_copy_dto import BookCopyDto
from books.infrastructure.http.dtos.update_book_dto import UpdateBookDTO
from books.infrastructure.http.dtos.book_dto import BookDto
from books.infrastructure.http.dtos.register_book_copy_dto import RegisterBookCopyDto
from books.infrastructure.http.dtos.register_book_dto import RegisterBookDto
from books.application.use_cases.get_book_recommendations import GetBookRecommendations
from books.infrastructure.di import get_book_recommendations_uc
from books.infrastructure.http.dtos.search_book_dto import AdvancedSearchBookDto, SearchBookDto
from shared.infrastructure.di import jwt_auth_guard
from users.domain.user import User
from users.domain.user_role import UserRole

router = APIRouter(prefix="/books",tags=["books"])

@router.get("/{book_id}")
async def search_book_by_id(
    book_id: int,
    get_book_by_id: GetBookById = Depends(get_search_book_by_id_uc)
):
    try:
        book : Book = await get_book_by_id.execute(book_id)
        return BookDto.to_dto(book)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="No se encontro el recurso solicitado"
        )


@router.post("/search")
async def basic_search_books(
    info: SearchBookDto,
    search_books: SearchBooks = Depends(get_search_book_uc)
):

    results: list[Book] = await search_books.execute(
        query=info.query,
        sort_by=info.sort_by,
        ascending=info.ascending,
        from_date=info.from_date,
        to_date=info.to_date,
        limit=info.limit + 1,
        offset=info.offset,
    )

    has_next = len(results) > info.limit
    if has_next:
        results = results[:info.limit]

    return {
        "result": [BookDto.to_dto(book) for book in results],
        "page": {
            "offset": info.offset,
            "limit": info.limit,
            "has_next": has_next,
        },
    }


@router.post("/advanced_search")
async def advanced_search_books(
    info: AdvancedSearchBookDto,
    advanced_search: AdvancedSearchBooks = Depends(get_advanced_search_book_uc),
):
    results: list[Book] = await advanced_search.execute(
        title=info.title,
        authors=info.authors,
        categories=info.category,
        isbn=info.isbn,
        language=info.language,
        editorial=info.editorial,
        sort_by=info.sort_by,
        ascending=info.ascending,
        from_date=info.from_date,
        to_date=info.to_date,
        limit=info.limit + 1,
        offset=info.offset,
    )

    has_next = len(results) > info.limit
    if has_next:
        results = results[:info.limit]

    return {
        "result": [BookDto.to_dto(book) for book in results],
        "page": {
            "offset": info.offset,
            "limit": info.limit,
            "has_next": has_next,
        },
    }

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

@router.patch("/{book_id}")
async def update_book(
    book_id: int,
    info: UpdateBookDTO,
    user: User = Depends(jwt_auth_guard),
    update_book: UpdateBook = Depends(get_updater_book_uc)
):
    if user.role != UserRole.BIBLIOTECARIO:
        raise HTTPException(
            status_code=403,
            detail="Solo bibliotecarios autorizados"
        )

    try:
        await update_book.execute(
            book_id,
            user.id.uid,
            title=info.title,
            isbn=info.isbn,
            description=info.description,
            editorial=info.editorial,
            publication_date=info.publication_date,
            cover_url=info.cover_url,
            language=info.language,
            authors=info.author,
            categories=info.category,
            page_count=info.page_count,
        )
    except Exception:
        raise HTTPException(
            status_code=409,
            detail="No se pudo actualizar el libro"
        )


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
