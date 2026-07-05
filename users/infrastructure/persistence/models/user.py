from __future__ import annotations
from shared.infrastructure.persistence.models.base import BaseModel
from users.domain.user_notification import NotificationType
from users.domain.user_role import UserRole
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loans.infrastructure.persistence.models.loan import Prestamo
    from loans.infrastructure.persistence.models.loan_request import SolicitudLibro

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

    nombre: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    numero_contacto: Mapped[str] = mapped_column(String(9))
    rol: Mapped[UserRole] = mapped_column(default=UserRole.LECTOR)
    hash_contrasena: Mapped[str] = mapped_column(String(255))

    prestamos: Mapped[list[Prestamo]] = relationship(back_populates="usuario",lazy='selectin')
    solicitudes: Mapped[list[SolicitudLibro]] = relationship(back_populates="usuario",lazy='selectin')
    notificaciones : Mapped[list["UsuarioSolicitudNotificationes"]] = relationship(back_populates="usuario")

class UsuarioSolicitudNotificationes(BaseModel):

    __tablename__ = "usuario_notificaciones"

    usuario_id : Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    solicitud_id : Mapped[int] = mapped_column(ForeignKey("solicitudes_libro.id"))
    tipo : Mapped[NotificationType] = mapped_column(nullable=False)

    solicitud : Mapped["SolicitudLibro"] = relationship(back_populates="notificaciones")
    usuario : Mapped["Usuario"] = relationship(back_populates="notificaciones")