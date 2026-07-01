from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from chatbot.domain.conversation import Conversation, ConversationId, ConversationStatus
from chatbot.domain.conversation_repository import ConversationRepository
from chatbot.domain.message import Message, ToolCall, ToolResult
from chatbot.infrastructure.persistence.conversation import ConversacionChat
from chatbot.infrastructure.persistence.message import MensajeChat
from shared.infrastructure.persistence.sql_drivers import async_session_factory
from users.domain.user_id import UserId


class SQLConversationRepository(ConversationRepository):

    async def load(self, user_id: UserId) -> Conversation | None:
        async with async_session_factory() as session:
            result = await session.execute(
                select(ConversacionChat)
                .where(
                    ConversacionChat.usuario_id == user_id.uid,
                    ConversacionChat.estado == ConversationStatus.ACTIVA,
                )
                .options(selectinload(ConversacionChat.mensajes))
                .order_by(ConversacionChat.id.desc())
                .limit(1)
            )
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return self._to_domain(row)

    async def save(self, conversation: Conversation) -> None:
        async with async_session_factory() as session:
            if conversation.id.id == 0:
                row = ConversacionChat(
                    usuario_id=conversation.user_id.uid,
                    estado=conversation.status,
                )
                session.add(row)
                await session.flush()
                await session.refresh(row)

                conversation.id.id = row.id
                conversation.created_at = row.created_at
                conversation.modified_at = row.updated_at

                for msg in conversation.history:
                    orm_msg = self._message_to_orm(msg)
                    orm_msg.conversacion_id = row.id
                    session.add(orm_msg)
                await session.flush()

            else:
                await session.execute(
                    delete(MensajeChat).where(
                        MensajeChat.conversacion_id == conversation.id.id
                    )
                )

                await session.execute(
                    update(ConversacionChat)
                    .where(ConversacionChat.id == conversation.id.id)
                    .values(
                        estado=conversation.status,
                    )
                )

                for msg in conversation.history:
                    orm_msg = self._message_to_orm(msg)
                    orm_msg.conversacion_id = conversation.id.id
                    session.add(orm_msg)
                await session.flush()

                result = await session.execute(
                    select(ConversacionChat).where(
                        ConversacionChat.id == conversation.id.id
                    )
                )
                row = result.scalar_one()
                conversation.modified_at = row.updated_at

    def _to_domain(self, row: ConversacionChat) -> Conversation:
        return Conversation(
            id=ConversationId(row.id),
            user_id=UserId(uid=row.usuario_id),
            history=[self._to_domain_message(m) for m in row.mensajes],
            status=row.estado,
            created_at=row.created_at,
            modified_at=row.updated_at,
        )

    def _to_domain_message(self, row: MensajeChat) -> Message:
        tool_calls: list[ToolCall] | None = None
        if row.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.get("id", ""),
                    name=tc.get("function", {}).get("name", ""),
                    arguments=tc.get("function", {}).get("arguments", {}),
                )
                for tc in row.tool_calls
            ]

        tool_results: list[ToolResult] | None = None
        if row.tool_results:
            tool_results = [
                ToolResult(tool_use_id=tr["tool_use_id"], content=tr["content"])
                for tr in row.tool_results
            ]

        return Message(
            role=row.rol,
            content=row.contenido,
            tool_calls=tool_calls,
            tool_call_id=row.tool_call_id,
            tool_results=tool_results,
        )

    def _message_to_orm(self, msg: Message) -> MensajeChat:
        return MensajeChat(
            rol=msg.role,
            contenido=msg.content,
            tool_calls=(
                [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": tc.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]
                if msg.tool_calls
                else None
            ),
            tool_call_id=msg.tool_call_id,
            tool_results=(
                [
                    {"tool_use_id": tr.tool_use_id, "content": tr.content}
                    for tr in msg.tool_results
                ]
                if msg.tool_results
                else None
            ),
        )
