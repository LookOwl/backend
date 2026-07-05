from sqlalchemy import any_, asc, desc, or_, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from books.domain.book import BookAuthor, BookCategory, BookCover, BookDescription, BookEditorial, BookISBN, BookId, BookLanguage, BookPageCount, BookPublicationDate, BookTitle
from books.domain.book_repository import BookRepository
from books.domain.book_search_criteria import AdvancedBookSearchCriteria, BookSearchCriteria, SortBy
from books.domain.result_page import ResultPage
from books.domain.book import Book
from books.infrastructure.persistence.models.author import Autor
from books.infrastructure.persistence.models.book import Libro
from books.infrastructure.persistence.models.genero import Genero
from books.infrastructure.persistence.models.book_copy import Ejemplar


_SORT_COLUMN = {
    SortBy.TITLE: Libro.titulo,
    SortBy.DATE: Libro.fecha_publicacion,
    SortBy.ID: Libro.id
}


class SQLBookRepository(BookRepository):
    async_session : AsyncSession
    def __init__(
            self,
            async_session : AsyncSession
    ) -> None:
        super().__init__()
        self.async_session = async_session

    async def get_by_id(self, book_id : BookId) -> Book | None:
        book = (await self.async_session.execute(
            select(Libro)
            .where(Libro.id == book_id.id, Libro.activo)
            .options(
                selectinload(Libro.autores),
                selectinload(Libro.generos)
            )
        )).scalar_one_or_none()
        if not book:
            return None
        return self._to_domain(book)

    async def search_book(
        self,
        search_criteria: BookSearchCriteria,
        page_limits : ResultPage
    ) -> list[Book]:

        stmt = (
            select(Libro)
            .options(
                selectinload(Libro.autores),
                selectinload(Libro.generos)
            )
            .join(Libro.autores)
            .join(Libro.generos)
            .where(Libro.activo)
            .where(
                or_(
                    Libro.titulo.ilike(f"%{search_criteria.query.query}%"),
                    Libro.editorial.ilike(f"%{search_criteria.query.query}%"),
                    Libro.isbn.ilike(f"%{search_criteria.query.query}%"),
                    Autor.nombre.ilike(f"%{search_criteria.query.query}%"),
                    Genero.nombre.ilike(f"%{search_criteria.query.query}%")
                )
            )
        )

        if search_criteria.from_date:
            stmt = stmt.where(search_criteria.from_date <= Libro.fecha_publicacion)

        if search_criteria.to_date:
            stmt = stmt.where(Libro.fecha_publicacion <= search_criteria.to_date)

        sort_column = _SORT_COLUMN[search_criteria.sort_by]
        stmt = stmt.order_by(asc(sort_column) if search_criteria.ascending else desc(sort_column))
        stmt = (
            stmt.distinct()
            .offset(page_limits.starts_at)
            .limit(page_limits.number_of_results)
        )

        books = await self.async_session.execute(stmt)
        books = books.scalars().all()
        return [self._to_domain(book) for book in books]

    async def advanced_search_book(
        self,
        search_criteria: AdvancedBookSearchCriteria,
        page_limits: ResultPage
    ) -> list[Book]:

        stmt = (
            select(Libro)
            .options(
                selectinload(Libro.autores),
                selectinload(Libro.generos)
            )
            .join(Libro.autores)
            .join(Libro.generos)
            .where(Libro.activo)
        )

        if search_criteria.title:
            stmt = stmt.where(
                Libro.titulo.ilike(f"%{search_criteria.title.title}%")
            )

        if search_criteria.isbn:
            stmt = stmt.where(
                Libro.isbn.ilike(f"%{search_criteria.isbn.isbn_code}%")
            )

        if search_criteria.language:
            stmt = stmt.where(Libro.lenguaje == search_criteria.language.lang)

        if search_criteria.editorial:
            stmt = stmt.where(
                Libro.editorial.ilike(f"%{search_criteria.editorial.editorial}%")
            )

        if search_criteria.authors and search_criteria.authors.authors:
            stmt = stmt.where(
                Autor.nombre.ilike(
                    any_(array(
                        [f"%{author}%" for author in search_criteria.authors.authors]
                    ))
                )
            )

        if search_criteria.category and search_criteria.category.categories:
            stmt = stmt.where(
                Genero.nombre.ilike(
                    any_(array(
                        [f"%{category}%" for category in search_criteria.category.categories]
                    ))
                )
            )

        if search_criteria.from_date:
            stmt = stmt.where(
                search_criteria.from_date <= Libro.fecha_publicacion
            )

        if search_criteria.to_date:
            stmt = stmt.where(
                Libro.fecha_publicacion <= search_criteria.to_date
            )

        sort_column = _SORT_COLUMN[search_criteria.sort_by]
        stmt = stmt.order_by(
            asc(sort_column) if search_criteria.ascending else desc(sort_column)
        )

        # Pagination
        stmt = (
            stmt.distinct()
            .offset(page_limits.starts_at)
            .limit(page_limits.number_of_results)
        )

        books = await self.async_session.execute(stmt)
        books = books.scalars().all()
        return [self._to_domain(book) for book in books]

    async def save_book(self, book : Book) -> BookId:
        # Resolve or create Autor/Genero objects while session is open
        resolved_autores = await self._resolve_autores(book.author.authors)
        resolved_generos = await self._resolve_generos(book.category.categories)

        libro = Libro(
            titulo=book.title.title,
            isbn=book.isbn.isbn_code if book.isbn else None,
            descripcion=book.description.description if book.description else None,
            editorial=book.editorial.editorial if book.editorial else None,
            fecha_publicacion=book.publication_date.pub_date if book.publication_date else None,
            url_portada=book.cover_url.url if book.cover_url else None,
            lenguaje=book.language.lang,
            num_paginas=book.page_count.count if book.page_count else None,
            autores=resolved_autores,
            generos=resolved_generos,
        )

        self.async_session.add(libro)
        await self.async_session.flush()
        await self.async_session.refresh(libro)
        return BookId(libro.id)

    async def update_book(self, book : Book) -> None:
        libro = await self.async_session.get(Libro, book.book_id.id)
        if not libro or not libro.activo:
            return

        resolved_autores = await self._resolve_autores(book.author.authors)
        resolved_generos = await self._resolve_generos(book.category.categories)

        libro.titulo = book.title.title
        libro.isbn = book.isbn.isbn_code if book.isbn else None
        libro.descripcion = book.description.description
        libro.editorial = book.editorial.editorial if book.editorial else None
        libro.fecha_publicacion = book.publication_date.pub_date if book.publication_date else None
        libro.url_portada = book.cover_url.url if book.cover_url else None
        libro.lenguaje = book.language.lang
        libro.num_paginas = book.page_count.count if book.page_count else None
        libro.autores = resolved_autores
        libro.generos = resolved_generos

        await self.async_session.flush()

    async def delete_book(self, book_id : BookId) -> None:
        await self.async_session.execute(
            update(Ejemplar)
            .where(Ejemplar.libro_id == book_id.id)
            .values(activo=False)
        )
        await self.async_session.execute(
            update(Libro)
            .where(Libro.id == book_id.id)
            .values(activo=False)
        )
        await self.async_session.flush()

    async def _resolve_autores(self, nombres: list[str]) -> list[Autor]:
        autores:list[Autor] = []
        for nombre in nombres:
            result = await self.async_session.execute(
                select(Autor).where(Autor.nombre == nombre)
            )
            autor = result.scalar_one_or_none()
            if not autor:
                autor = Autor(nombre=nombre)
                self.async_session.add(autor)
                await self.async_session.flush()
            await self.async_session.refresh(autor)
            autores.append(autor)
        return autores

    async def _resolve_generos(self, nombres: list[str]) -> list[Genero]:
        generos : list[Genero] = []
        for nombre in nombres:
            result = await self.async_session.execute(
                select(Genero).where(Genero.nombre == nombre)
            )
            genero = result.scalar_one_or_none()
            if not genero:
                genero = Genero(nombre=nombre)
                self.async_session.add(genero)
            await self.async_session.flush()
            await self.async_session.refresh(genero)
            generos.append(genero)
        return generos

    def _to_domain(self, book: Libro) -> Book:
        return Book(
                BookId(book.id),
                BookTitle(book.titulo),
                BookISBN(book.isbn) if book.isbn else None ,
                BookDescription(book.descripcion),
                BookEditorial(book.editorial) if book.editorial else None,
                BookPublicationDate(book.fecha_publicacion) if book.fecha_publicacion else None,
                BookCover(book.url_portada) if book.url_portada else None ,
                BookLanguage(book.lenguaje),
                BookAuthor([autor.nombre for autor in book.autores]),
                BookCategory([genero.nombre for genero in book.generos]),
                page_count=BookPageCount(book.num_paginas) if book.num_paginas else None
            )
