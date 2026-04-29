from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from db.base import BaseModel

class Genero (BaseModel):
    """
        Modelo ORM para representar géneros de libros.

        Atributos:
            - nombre: Nombre del género correspondiente.
    """

    __tablename__ = "generos"

    nombre: Mapped[str] = mapped_column(String(100), unique=True)
