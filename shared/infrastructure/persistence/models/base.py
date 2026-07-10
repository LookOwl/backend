from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column
from sqlalchemy import Integer, DateTime, func
from typing import Annotated

# Anotaciones reutilizables entre tablas
intpk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]

class Base(DeclarativeBase):
    """
        Modelo de construcción para ORM minimalista.
    """
    pass

class BaseModel(Base):

    """
        Modelo base para construir ORM junto a atributos base.

        Atributos:
            - id: Identificador único para tabla de una entidad.
            - created_at: Fecha de creación de la entidad.
            - updated_at: Fecha de la última actualización realizada.
    """

    __abstract__ = True

    id: MappedColumn[intpk]
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())
