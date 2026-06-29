from sqlalchemy import any_, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession

from books.domain.book import BookAuthor, BookCategory, BookCover, BookDescription, BookEditorial, BookISBN, BookId, BookLanguage, BookPageCount, BookPublicationDate, BookTitle
from books.domain.book_repository import BookRepository
from books.domain.book_search_criteria import BookSearchCriteria
from books.domain.result_page import ResultPage
from books.domain.book import Book
from books.infrastructure.persistence.models.author import Autor
from books.infrastructure.persistence.models.book import Libro
from books.infrastructure.persistence.models.genero import Genero
from books.infrastructure.persistence.models.book_copy import Ejemplar


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

    async def find_by_criteria(self, book_criteria : BookSearchCriteria, page_limits : ResultPage) -> list[Book]:
        query = select(Libro).options(
            selectinload(Libro.autores),
            selectinload(Libro.generos),
        )

        query = query.where(Libro.activo)

        if book_criteria.title:
            query = query.where(Libro.titulo.ilike(f"%{book_criteria.title.title}%"))

        if book_criteria.language:
            query = query.where(Libro.lenguaje == book_criteria.language.lang)

        if len(book_criteria.authors.authors) > 0:
            query = query.join(Libro.autores).where(
                Autor.nombre.ilike(
                    any_(array(
                        [f"%{author}%" for author in book_criteria.authors.authors]
                    ))
                )
            )

        if len(book_criteria.category.categories) > 0:
            query = query.join(Libro.generos).where(
                Genero.nombre.ilike(any_(array(
                        [f"%{category}%" for category in book_criteria.category.categories]
                    ))
                )
            )

        if book_criteria.from_date:
            query = query.where(book_criteria.from_date <= Libro.fecha_publicacion)

        if book_criteria.to_date:
            query = query.where(Libro.fecha_publicacion <= book_criteria.to_date)

        query = query.distinct().order_by(Libro.id).offset(page_limits.starts_at).limit(page_limits.number_of_results)
        result = await self.async_session.execute(query)
        libros = list(result.scalars().all())
        return [
            self._to_domain(book)
            for book in libros
        ]

    async def save_book(self, book : Book) -> None:
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
        return

    async def update_book(self, book : Book) -> None:
        resolved_autores = await self._resolve_autores(book.author.authors)
        resolved_generos = await self._resolve_generos(book.category.categories)
        await self.async_session.execute(
            update(Libro)
            .where(Libro.id == book.book_id.id)
            .values(
                titulo = book.title.title,
                isbn = book.isbn.isbn_code if book.isbn else None,
                descripcion = book.description.description if book.description else None,
                editorial = book.editorial.editorial if book.editorial else None,
                fecha_publicacion = book.publication_date.pub_date if book.publication_date else None,
                url_portada = book.cover_url.url if book.cover_url else None,
                lenguaje = book.language.lang,
                num_paginas = book.page_count.count if book.page_count else None,
                autores = resolved_autores,
                generos = resolved_generos,
            )
        )
        await self.async_session.flush()
        return

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
