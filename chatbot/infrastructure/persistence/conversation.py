from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from chatbot.domain.conversation import ConversationStatus
from shared.infrastructure.persistence.models.base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatbot.infrastructure.persistence.message import MensajeChat
    from users.infrastructure.persistence.models.user import Usuario


class ConversacionChat(BaseModel):

    """
        Modelo ORM para representar una conversación del chatbot.

        Atributos:
            - usuario_id: Identificador del usuario asociado a la conversación.
            - estado: Estado actual de la conversación (ACTIVA, CERRADA).
    """

    __tablename__ = "conversaciones_chat"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    estado: Mapped[ConversationStatus] = mapped_column(default=ConversationStatus.ACTIVA)

    usuario: Mapped[Usuario] = relationship(lazy="joined")
    mensajes: Mapped[list[MensajeChat]] = relationship(
        back_populates="conversacion",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="MensajeChat.created_at",
    )
