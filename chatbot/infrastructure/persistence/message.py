from __future__ import annotations
from sqlalchemy import ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from chatbot.domain.message import MessageRole
from shared.infrastructure.persistence.models.base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatbot.infrastructure.persistence.conversation import ConversacionChat


class MensajeChat(BaseModel):

    """
        Modelo ORM para representar un mensaje dentro de una conversación.

        Atributos:
            - conversacion_id: Identificador de la conversación a la que pertenece.
            - rol: Rol del emisor (user, assistant, system, tool).
            - contenido: Contenido textual del mensaje (puede ser nulo si solo hay tool_calls).
            - tool_calls: Llamadas a herramientas solicitadas por el LLM (JSON).
            - tool_call_id: ID de la llamada a herramienta a la que responde (solo rol TOOL, legacy).
            - tool_results: Resultados agrupados de herramientas (JSON), usado por el rol TOOL.
    """

    __tablename__ = "mensajes_chat"

    conversacion_id: Mapped[int] = mapped_column(
        ForeignKey("conversaciones_chat.id"),
    )
    rol: Mapped[MessageRole] = mapped_column()
    contenido: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tool_calls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tool_call_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    tool_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    conversacion: Mapped[ConversacionChat] = relationship(
        back_populates="mensajes",
    )
