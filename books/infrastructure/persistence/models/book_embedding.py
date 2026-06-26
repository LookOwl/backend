from __future__ import annotations
from sqlalchemy import ForeignKey, Index, String
from shared.infrastructure.persistence.models.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import VECTOR  #type: ignore (pgvector does not come with .pyi files)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from books.infrastructure.persistence.models.book import Libro



class LibroEmbedding(BaseModel):

    """
        Modelo ORM para representar embeddings de un libro.

        Atributos:
            - id_libro: Identificador del perfil de libro que representa
            - embedding: Vector principal que corresponde al libro
            - model: Nombre del modelo de IA usado para la generación del embedding

    """
    __tablename__ = "libro_embeddings"

    __table_args__ = (
            Index(
                "ix_libro_embeddings_hnsw",
                "embedding",
                postgresql_using="hnsw",
                postgresql_with={"m": 16, "ef_construction": 64},
                postgresql_ops={"embedding": "vector_cosine_ops"}
            ),
        )

    id_libro: Mapped[int] = mapped_column(ForeignKey("libros.id"))
    embedding: Mapped[VECTOR] = mapped_column(VECTOR(384))
    model: Mapped[str] = mapped_column(String(50))

    libro: Mapped[Libro] = relationship(back_populates="embedding")
