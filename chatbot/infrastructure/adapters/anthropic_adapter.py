from anthropic import AsyncAnthropic
from anthropic.types import (
    MessageParam,
    TextBlockParam,
    ToolParam,
    ToolResultBlockParam,
    ToolUseBlock,
    ToolUseBlockParam,
)
from chatbot.application.ports import LLMPort
from chatbot.domain.message import Message, MessageRole, ToolCall
from chatbot.domain.tools import LLMResponse, ToolDefinition


SYSTEM_PROMPT = """
Eres un asistente virtual especializado y exclusivo de la biblioteca. Tu único propósito es ayudar a los usuarios a encontrar libros y recomendar lecturas utilizando las herramientas que tienes disponibles. No eres un asistente general; eres un motor de búsqueda conversacional y un recomendador literario.

**Reglas estrictas e inquebrantables:**

1. **Alcance limitado:** Solo puedes responder preguntas relacionadas con la búsqueda y recomendación de libros. Si el usuario pregunta sobre cualquier tema ajeno a esto (clima, noticias, política, deportes, matemáticas, recetas, etc.), debes rechazar cortésmente la pregunta y redirigir tu enfoque.

2. **Formato de rechazo:** Cuando un usuario salga del tema, responde usando exactamente esta plantilla:
> "Lo siento, soy un asistente especializado únicamente en el catálogo y recomendaciones de libros. No puedo responder sobre [tema de la pregunta]. ¿Te gustaría que te ayude a buscar un libro o que te dé una recomendación personalizada?"

3. **Uso obligatorio de las herramientas:** No inventes títulos, autores ni disponibilidad. Toda la información sobre libros debe obtenerse a través de las herramientas que se te proporcionan. Debes decidir cuál usar según la intención del usuario:

   - **`search_books`** → Úsala **siempre** que el usuario proporcione un **título concreto, un autor específico o una palabra clave de género/categoría** (ej. "trilogía de El problema de los tres cuerpos", "libros de Stephen King", "fantasía épica"). Esta herramienta sirve para buscar en el catálogo.

   - **`recommend_books_by_query`** → Úsala cuando el usuario pida recomendaciones basadas en una **descripción en lenguaje natural**, sin mencionar un libro de referencia concreto (ej. "quiero algo de terror cósmico", "novelas de ciencia ficción distópica con personajes femeninos fuertes", "buscas un libro parecido a la película Origen").

   - **`recommend_books_by_id`** → Úsala cuando el usuario quiera **libros similares a uno que ya ha leído o mencionado explícitamente** (ej. "recomiéndame algo como 'Cien años de soledad'", "quiero libros parecidos a Fundación").
     *Importante:* Como esta herramienta requiere un ID numérico y el usuario normalmente te dará un título, **primero debes ejecutar `search_books` con ese título** para obtener su ID. Si `search_books` devuelve varias coincidencias, pregunta al usuario cuál de ellas es la correcta antes de llamar a `recommend_books_by_id`. Si el usuario te da directamente un número de ID, úsalo sin más.

4. **Prohibición de inventar datos:** Si una herramienta no devuelve resultados, no inventes libros. Simplemente indica que no se encontraron coincidencias y sugiere al usuario que reformule su consulta o que pruebe con otro término.

5. **Tono y estilo:** Responde siempre en español claro y conciso. Si el usuario te saluda o agradece, responde con cordialidad pero ve directamente al grano. Si la consulta es ambigua o puede interpretarse para varias herramientas, pide aclaraciones usando preguntas cerradas o de opción múltiple para guiar al usuario (ej. "¿Buscas un título exacto o prefieres que te recomiende algo similar?").
"""


class AnthropicAdapter(LLMPort):

    def __init__(
        self,
        client: AsyncAnthropic,
        model: str = "deepseek-v4-flash"
    ) -> None:
        self._client = client
        self._model = model

    async def generate_response(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
    ) -> LLMResponse:
        anthropic_messages = [self._to_anthropic_message(m) for m in messages]
        anthropic_tools = self._to_anthropic_tools(tools) if tools else None

        kwargs: dict = {
            "model": self._model,
            "messages": anthropic_messages,
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
        }
        if anthropic_tools:
            kwargs["tools"] = anthropic_tools

        response = await self._client.messages.create(**kwargs)
        return self._parse_response(response)

    def _to_anthropic_message(self, msg: Message) -> MessageParam:
        if msg.role == MessageRole.USER:
            return MessageParam(role="user", content=msg.content or "")

        if msg.role == MessageRole.ASSISTANT:
            if msg.tool_calls:
                assistant_blocks: list[TextBlockParam | ToolUseBlockParam] = []
                if msg.content:
                    assistant_blocks.append(TextBlockParam(type="text", text=msg.content))
                for tc in msg.tool_calls:
                    assistant_blocks.append(
                        ToolUseBlockParam(
                            type="tool_use",
                            id=tc.id,
                            name=tc.name,
                            input=tc.arguments,
                        )
                    )
                return MessageParam(role="assistant", content=assistant_blocks)
            else:
                return MessageParam(role="assistant", content=msg.content or "")

        if msg.role == MessageRole.TOOL:
            if msg.tool_results:
                tool_blocks: list[ToolResultBlockParam] = []
                for tr in msg.tool_results:
                    tool_blocks.append(
                        ToolResultBlockParam(
                            type="tool_result",
                            tool_use_id=tr.tool_use_id,
                            content=tr.content,
                        )
                    )
                return MessageParam(role="user", content=tool_blocks)

        raise ValueError(f"Unexpected message role: {msg.role}")

    def _to_anthropic_tools(self, tools: list[ToolDefinition]) -> list[ToolParam]:
        result: list[ToolParam] = []
        for tool in tools:
            anthropic_tool: ToolParam = {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters,
            }
            result.append(anthropic_tool)
        return result

    def _parse_response(self, response) -> LLMResponse:
        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use" and isinstance(block, ToolUseBlock):
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=dict(block.input) if hasattr(block.input, "items") else block.input,
                    )
                )

        if tool_calls:
            return LLMResponse(type="tool_calls", tool_calls=tool_calls)

        return LLMResponse(type="text", content="".join(text_parts))
