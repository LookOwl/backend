from sqlalchemy.orm import Session
from sqlalchemy import select
from sentence_transformers import SentenceTransformer
from db.models.libro_embedding import LibroEmbedding
from domain.book import Book
from repositories.book_repository import BookRepository

MODEL_NAME = "AventIQ-AI/all-MiniLM-L6-v2-book-recommendation-system"
_model = SentenceTransformer(MODEL_NAME)


class BookEmbeddingRepository:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.book_repo = BookRepository(self.db)

    def create(self, book_id: int, title: str, description: str, categories: list[str]) -> None:
        text = f"{title} {description} Etiquetas: {' '.join(categories)}"
        embedding = _model.encode(text).tolist()

        libro_embedding = LibroEmbedding(
            id_libro=book_id,
            embedding=embedding,
            model=MODEL_NAME,
        )
        self.db.add(libro_embedding)
        self.db.commit()

    def get_recommendations(self, book_id: int, num_recommendations: int = 15) -> list[Book]:
        source = self.db.execute(
            select(LibroEmbedding).where(LibroEmbedding.id_libro == book_id)
        ).scalars().first()

        if source is None:
            return []

        stmt = (
            select(LibroEmbedding)
            .where(LibroEmbedding.id_libro != book_id)
            .order_by(LibroEmbedding.embedding.cosine_distance(source.embedding))
            .limit(num_recommendations)
        )
        results = self.db.execute(stmt).scalars().all()

        return [self.book_repo._to_domain(result.libro) for result in results]
