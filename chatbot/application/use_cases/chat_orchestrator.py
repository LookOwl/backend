from datetime import datetime, timedelta, timezone
from chatbot.application.ports import ChatInputPort, LLMPort, TokenCounterPort, ToolExecutorPort
from chatbot.domain.conversation import Conversation, ConversationId, ConversationStatus
from chatbot.domain.message import Message, MessageRole, ToolResult
from chatbot.domain.conversation_repository import ConversationRepository
from chatbot.domain.tools import LLMResponse, ToolDefinition
from shared.application.unit_of_work import UnitOfWork
from users.domain.user_id import UserId


class ChatOrchestrator(ChatInputPort):

    MAX_TOKENS = 8192  # Ventana de contexto límite para un LLM

    def __init__(
        self,
        repo: ConversationRepository,
        llm: LLMPort,
        token_counter: TokenCounterPort,
        tool_executor: ToolExecutorPort,
        uow: UnitOfWork,
    ) -> None:
        self.repo = repo
        self.llm = llm
        self.token_counter = token_counter
        self.tool_executor = tool_executor
        self.uow = uow
        self._tools = self._register_tools()

    async def process_user_message(self, user_id: UserId, user_input: str) -> str:
        async with self.uow:
            conv = await self._load_or_create(user_id)
            conv.add_message(Message(role=MessageRole.USER, content=user_input))
            final_answer = await self._run_llm_loop(conv)
            await self.repo.save(conv)
        return final_answer

    async def _run_llm_loop(self, conv: Conversation) -> str:
        while True:
            # Llamada corriente a LLM
            messages_for_llm = self._prepare_context(conv)
            llm_response: LLMResponse = await self.llm.generate_response(messages_for_llm, self._tools)

            # Verificación de texto o llamada a herramienta
            if llm_response.type == "text":
                final_answer = llm_response.content or ""
                conv.add_message(Message(role=MessageRole.ASSISTANT, content=final_answer))
                return final_answer

            if llm_response.type == "tool_calls" and llm_response.tool_calls:
                conv.add_message(
                    Message(
                        role=MessageRole.ASSISTANT,
                        content=None,
                        tool_calls=llm_response.tool_calls,
                    )
                )

                # Ejecutar todas las herramientas y agrupar resultados en un solo mensaje
                tool_results: list[ToolResult] = []
                for tool_call in llm_response.tool_calls:
                    result = await self.tool_executor.execute(tool_call)
                    tool_results.append(ToolResult(tool_use_id=tool_call.id, content=result))

                conv.add_message(
                    Message(
                        role=MessageRole.TOOL,
                        content=None,
                        tool_results=tool_results,
                    )
                )

    def _prepare_context(self, conv: Conversation) -> list[Message]:
        """
        Acorta el historial de mensajes en base a la ventana de contexto definida.
        """
        messages = conv.history
        total_tokens = self.token_counter.count(messages)

        while total_tokens > self.MAX_TOKENS and messages:
            messages.pop(0)
            total_tokens = self.token_counter.count(messages)

        return messages

    def _register_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="search_books",
                description="Busca libros en el catálogo de la biblioteca usando texto libre. "
                            "Realiza una búsqueda en múltiples campos: título, autor, editorial, ISBN y categoría. "
                            "Útil cuando el usuario da un título, nombre de autor o cualquier palabra clave.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Texto libre para buscar libros (título, autor, editorial, ISBN o categoría)",
                        }
                    },
                    "required": ["query"],
                },
            ),
            ToolDefinition(
                name="recommend_books_by_query",
                description="Obtiene recomendaciones de libros basadas en una búsqueda semántica (ej. 'novelas de ciencia ficción distópica')",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Descripción en lenguaje natural del tipo de libros que el usuario desea",
                        }
                    },
                    "required": ["query"],
                },
            ),
            ToolDefinition(
                name="recommend_books_by_id",
                description="Obtiene recomendaciones de libros similares a un libro específico por su ID",
                parameters={
                    "type": "object",
                    "properties": {
                        "book_id": {
                            "type": "integer",
                            "description": "El ID numérico del libro de referencia",
                        }
                    },
                    "required": ["book_id"],
                },
            )
        ]

    async def _load_or_create(self, user_id: UserId) -> Conversation:
        """
        Carga una conversación activa para el usuario, o crea una nueva.
        Si la conversación supera las 2 horas de inactividad, se cierra
        automáticamente y se inicia una nueva.
        """
        existing = await self.repo.load(user_id)
        if existing and existing.status == ConversationStatus.ACTIVA:
            if (existing.modified_at and (datetime.now(timezone.utc) - existing.modified_at) > timedelta(hours=2)):
                existing.close()
                await self.repo.save(existing)
            else:
                return existing

        # Crea conversación nueva con id transitorio
        conv = Conversation(
            id=ConversationId(id=0),
            user_id=user_id,
        )

        return conv
