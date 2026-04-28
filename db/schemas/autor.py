from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from db.base import BaseModel

class Autor(BaseModel):

    """
        Modelo ORM para representar un autor

        Atributos:
            - nombre: Nombre completo del autor.
    """

    __tablename__ = "autores"

    nombre: Mapped[str] = mapped_column(String(255))
