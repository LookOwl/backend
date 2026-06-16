from __future__ import annotations
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Table, Text, Column, ForeignKey
from typing import Optional

from shared.infrastructure.persistence.models.base import Base, BaseModel
from books.infrastructure.persistence.models.author import Autor
from books.infrastructure.persistence.models.genero import Genero
from loans.infrastructure.persistence.models.loan_request import SolicitudLibro
from books.infrastructure.persistence.models.book_embedding import LibroEmbedding

from books.infrastructure.persistence.models.book_copy import Ejemplar


libro_autores = Table("libro_autores", Base.metadata,
    Column("libro_id", ForeignKey("libros.id"), primary_key=True), #type: ignore
    Column("autor_id", ForeignKey("autores.id"), primary_key=True) #type: ignore
)

libro_generos = Table("libro_generos", Base.metadata,
    Column("libro_id", ForeignKey("libros.id"), primary_key=True), #type: ignore
    Column("genero_id", ForeignKey("generos.id"), primary_key=True) #type: ignore
)

class Libro(BaseModel):

    """
        Modelo ORM para representar un libro.

        Atributos:
            - titulo: Titulo del libro.
            - isbn: Identificador global del libro.
            - descripcion: Descripción o sinopsis de los contenidos del libro.
            - editorial: Nombre de la editorial de publicación del libro.
            - fecha_publicacion: Fecha de publicación del libro.
            - url_portada: URL para la recuperación de imagen de portada.
            - lenguaje: Idioma del libro registrado, por defecto español ("es")
            - num_paginas: Número de páginas del libro.
    """

    __tablename__ = "libros"

    titulo: Mapped[str] = mapped_column(String(255))
    isbn: Mapped[Optional[str]] = mapped_column(String(13), unique=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    editorial: Mapped[Optional[str]] = mapped_column(String(100))
    fecha_publicacion: Mapped[Optional[date]]
    url_portada: Mapped[Optional[str]] = mapped_column(String(500))
    lenguaje: Mapped[str] = mapped_column(String(2), default="es")
    num_paginas: Mapped[Optional[int]]

    autores: Mapped[list[Autor]] = relationship(secondary=libro_autores, lazy="selectin")
    generos: Mapped[list[Genero]] = relationship(secondary=libro_generos, lazy="selectin")
    ejemplares: Mapped[list[Ejemplar]] = relationship(back_populates="libro")
    solicitudes: Mapped[list[SolicitudLibro]] = relationship(back_populates="libro")
    embedding: Mapped[LibroEmbedding] = relationship(back_populates="libro")
