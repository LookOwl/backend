from sqlalchemy import select
from sqlalchemy.orm import Session
from db.models.autor import Autor
from db.models.genero import Genero
from db.models.libro import Libro
from domain.book import Book
from datetime import date

class BookRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    # TODO: Mejorar el retorno de libros con filtros y búsqueda
    def get_books(self) -> list[Book]:
        libros = list(self.db.execute(select(Libro)).scalars().all())
        return [self._to_domain(libro) for libro in libros]

    def save_book(self, book: Book) -> Book:
        libro = Libro(
            id = book.uid,
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
            uid = str(libro.id),
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
            n_copies = 1, # TODO: Crear tablas y asignaciones para más libros
        )
