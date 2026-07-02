import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]

from books.domain.book import Book, BookAuthor, BookCategory, BookCover, BookDescription, BookEditorial, BookISBN, BookId, BookLanguage, BookPageCount, BookPublicationDate, BookTitle
from books.infrastructure.persistence.models.book import Libro
from books.infrastructure.persistence.models.book_embedding import LibroEmbedding
from books.domain.book_embedding_repository import BookEmbeddingRepository
from shared.infrastructure.settings import settings

_MODEL_NAME = "AventIQ-AI/all-MiniLM-L6-v2-book-recommendation-system"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the sentence transformer model on first use."""
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME, token=settings.HUGGINGFACE_KEY)
    return _model


class SQLBookEmbeddingRepository(BookEmbeddingRepository):
    async_session: AsyncSession

    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    async def save(self, book_id: BookId, prompt: str) -> None:
        model = _get_model()
        prompt_embedding = await asyncio.to_thread(model.encode, prompt)

        libro_embedding = LibroEmbedding(
            id_libro=book_id.id,
            embedding=prompt_embedding.tolist(),
            model=_MODEL_NAME
        )

        self.async_session.add(libro_embedding)
        await self.async_session.flush()
        await self.async_session.refresh(libro_embedding)

        return

    async def get_recommendations_by_book(
        self, book_id: BookId, num_recommendations: int = 15
    ) -> list[Book]:
        source_result = await self.async_session.execute(
            select(LibroEmbedding).where(LibroEmbedding.id_libro == book_id.id)
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
            .where(LibroEmbedding.id_libro != book_id.id)
            .order_by(LibroEmbedding.embedding.cosine_distance(source.embedding))
            .limit(num_recommendations)
        )
        results = await self.async_session.execute(stmt)

        return [self._to_domain(result.libro) for result in results.scalars().all()]

    async def get_recommendations_by_query(
        self, query: str, num_recommendations: int = 15
    ) -> list[Book]:
        model = _get_model()
        query_embedding = await asyncio.to_thread(model.encode, query)

        stmt = (
            select(LibroEmbedding)
            .options(
                selectinload(LibroEmbedding.libro).selectinload(Libro.autores),
                selectinload(LibroEmbedding.libro).selectinload(Libro.generos),
            )
            .order_by(
                LibroEmbedding.embedding.cosine_distance(query_embedding.tolist())
            )
            .limit(num_recommendations)
        )
        results = await self.async_session.execute(stmt)

        return [self._to_domain(result.libro) for result in results.scalars().all()]

    def _to_domain(self, libro: Libro) -> Book:
        return Book(
            book_id=BookId(libro.id),
            title=BookTitle(libro.titulo),
            isbn=BookISBN(libro.isbn) if libro.isbn else None,
            description=BookDescription(libro.descripcion) if libro.descripcion else BookDescription(""),
            editorial=BookEditorial(libro.editorial) if libro.editorial else None,
            publication_date=BookPublicationDate(libro.fecha_publicacion) if libro.fecha_publicacion else None,
            cover_url=BookCover(libro.url_portada) if libro.url_portada else None,
            language=BookLanguage(libro.lenguaje),
            author=BookAuthor([autor.nombre for autor in libro.autores]),
            category=BookCategory([genero.nombre for genero in libro.generos]),
            page_count=BookPageCount(libro.num_paginas) if libro.num_paginas else None,
        )
