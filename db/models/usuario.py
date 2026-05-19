from __future__ import annotations
from db.base import BaseModel
from domain.enums.roles_usuario import RolUsuario
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.prestamo import Prestamo

class Usuario(BaseModel):

    """
        Modelo ORM para representar un usuario.

        Atributos:
            - nombre: Nombre del usuario.
            - email: Correo electrónico del usuario.
            - numero_contacto: Número telefónico de contacto para el usuario.
            - rol: Tipo de cargo asignado a cada usuario (bibliotecario o lector)
            - password_hashed: Hash guardado de la contraseña
    """

    __tablename__ = "usuarios"

    nombre: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(30))
    numero_contacto: Mapped[str] = mapped_column(String(11))
    rol: Mapped[RolUsuario] = mapped_column(default=RolUsuario.LECTOR)
    hash_contrasena: Mapped[str] = mapped_column(String(255))

    prestamos: Mapped[list[Prestamo]] = relationship(back_populates="usuario")
