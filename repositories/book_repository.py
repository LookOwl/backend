from sqlalchemy import select
from sqlalchemy.orm import Session
from db.models.autor import Autor
from db.models.genero import Genero
from db.models.libro import Libro
from domain.book import Book
from datetime import date
from typing import Optional

class BookRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_books(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        language: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[Book]:
        query = select(Libro)

        if title:
            query = query.where(Libro.titulo.ilike(f"%{title}%"))

        if language:
            query = query.where(Libro.lenguaje == language)

        if author:
            query = query.join(Libro.autores).where(
                Autor.nombre.ilike(f"%{author}%")
            )

        if genre:
            query = query.join(Libro.generos).where(
                Genero.nombre.ilike(f"%{genre}%")
            )

        if from_date:
            query = query.where(from_date <= Libro.fecha_publicacion)

        if to_date:
            query = query.where(Libro.fecha_publicacion <= to_date)

        query = query.distinct().offset(offset).limit(limit)
        libros = list(self.db.execute(query).scalars().all())
        return [self._to_domain(libro) for libro in libros]

    def save_book(self, book: Book) -> Book:
        self._validate_book(book)
        libro = Libro(
            titulo = book.title,
            isbn = book.isbn,
            descripcion = book.description,
            editorial = book.editorial,
            fecha_publicacion = book.publication_date,
            url_portada = book.cover_url,
            lenguaje = book.language,
            num_paginas = book.page_count,
            autores = self._resolve_autores(book.author),
            generos = self._resolve_generos(book.category)
        )
        self.db.add(libro)
        self.db.commit()
        self.db.refresh(libro)
        return self._to_domain(libro)

    def _validate_book(self, book: Book) -> None:
        if not book.title or len(book.title) > 255:
            raise ValueError("El titulo del libro no es valido")
        if book.isbn and len(book.isbn) > 13:
            raise ValueError("El ISBN del libro no es valido")
        if book.editorial and len(book.editorial) > 100:
            raise ValueError("La editorial del libro no es valida")
        if book.cover_url and len(book.cover_url) > 500:
            raise ValueError("La URL de portada no es valida")
        if book.language and len(book.language) != 2:
            raise ValueError("El lenguaje del libro no es valido")

    def _resolve_autores(self, nombres: list[str]) -> list[str]:
        autores = []
        for nombre in nombres:
            autor = self.db.execute(
                select(Autor).where(Autor.nombre == nombre)
            ).scalar_one_or_none()
            if not autor:
                autor = Autor(nombre=nombre)
                self.db.add(autor)
            autores.append(autor)
        return autores

    def _resolve_generos(self, nombres: list[str]):
        generos = []
        for nombre in nombres:
            genero = self.db.execute(
                select(Genero).where(Genero.nombre == nombre)
            ).scalar_one_or_none()
            if not genero:
                genero = Genero(nombre=nombre)
                self.db.add(genero)
            generos.append(genero)
        return generos

    def _to_domain(self, libro: Libro) -> Book:
        return Book(
            uid = libro.id,
            title = libro.titulo,
            isbn = libro.isbn if libro.isbn else "",
            description = libro.descripcion if libro.descripcion else "",
            editorial = libro.editorial if libro.editorial else "",
            publication_date = libro.fecha_publicacion if libro.fecha_publicacion else date(0, 0, 0),
            cover_url = libro.url_portada if libro.url_portada else "",
            language = libro.lenguaje,
            author = [autor.nombre for autor in libro.autores],
            category = [genero.nombre for genero in libro.generos],
            page_count = libro.num_paginas if libro.num_paginas else -1,
        )
