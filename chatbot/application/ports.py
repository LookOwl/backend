from abc import ABC, abstractmethod
from chatbot.domain.message import Message, ToolCall
from chatbot.domain.tools import ToolDefinition, LLMResponse
from users.domain.user_id import UserId


class ChatInputPort(ABC):
    """Puerto de entrada: cómo el mundo exterior (HTTP, WebSocket, CLI) se comunica con el núcleo."""

    @abstractmethod
    async def process_user_message(self, user_id: UserId, user_input: str) -> str:
        pass


class LLMPort(ABC):
    """Puerto para la generación de respuestas mediante un servicio externo IA/LLM"""

    @abstractmethod
    async def generate_response(
        self, messages: list[Message], tools: list[ToolDefinition]
    ) -> LLMResponse:
        pass


class TokenCounterPort(ABC):
    """Puerto para el conteo de tokens, va de la mano con la declaración del servicio de generación de respuestas para manejo de ventanas de contexto"""

    @abstractmethod
    def count(self, messages: list[Message]) -> int:
        pass


class ToolExecutorPort(ABC):
    """Puerto para la ejecución de llamadas a herramientas/funciones solicitadas por el LLM."""

    @abstractmethod
    async def execute(self, tool_call: ToolCall) -> str:
        pass
