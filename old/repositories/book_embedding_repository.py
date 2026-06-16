from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sentence_transformers import SentenceTransformer
from old.infrastructure.database.models.libro_embedding import LibroEmbedding
from old.infrastructure.database.models.libro import Libro
from old.domain.book import Book
from datetime import date
from old.infrastructure.config.config import settings
import asyncio

MODEL_NAME = "AventIQ-AI/all-MiniLM-L6-v2-book-recommendation-system"
_model = SentenceTransformer(MODEL_NAME, token=settings.HUGGINGFACE_KEY)


class BookEmbeddingRepository:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, book_id: int, title: str, description: str, categories: list[str]) -> None:
        text = f"{title} {description} Etiquetas: {' '.join(categories)}"
        embedding = (await asyncio.to_thread(_model.encode, text)).tolist()

        libro_embedding = LibroEmbedding(
            id_libro=book_id,
            embedding=embedding,
            model=MODEL_NAME,
        )
        self.db.add(libro_embedding)

    async def get_recommendations(self, book_id: int, num_recommendations: int = 15) -> list[Book]:
        source_result = await self.db.execute(
            select(LibroEmbedding).where(LibroEmbedding.id_libro == book_id)
        )
        source = source_result.scalars().first()

        if source is None:
            return []

        stmt = (
            select(LibroEmbedding)
            .options(
                selectinload(LibroEmbedding.libro).selectinload(Libro.autores),
                selectinload(LibroEmbedding.libro).selectinload(Libro.generos),
            )
            .where(LibroEmbedding.id_libro != book_id)
            .order_by(LibroEmbedding.embedding.cosine_distance(source.embedding))
            .limit(num_recommendations)
        )
        results = await self.db.execute(stmt)

        return [self._to_domain(result.libro) for result in results.scalars().all()]

    def _to_domain(self, libro: Libro) -> Book:
        return Book(
            id=libro.id,
            title=libro.titulo,
            isbn=libro.isbn if libro.isbn else "",
            description=libro.descripcion if libro.descripcion else "",
            editorial=libro.editorial if libro.editorial else "",
            publication_date=libro.fecha_publicacion if libro.fecha_publicacion else date.min,
            cover_url=libro.url_portada if libro.url_portada else "",
            language=libro.lenguaje,
            author=[autor.nombre for autor in libro.autores],
            category=[genero.nombre for genero in libro.generos],
            page_count=libro.num_paginas if libro.num_paginas else -1,
        )
