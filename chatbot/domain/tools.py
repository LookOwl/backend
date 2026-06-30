from dataclasses import dataclass
from typing import Literal
from chatbot.domain.message import ToolCall


@dataclass
class ToolDefinition:
    """
    Contrato de definición de herramienta implementada por algun otro proveedor
    """

    name: str
    description: str
    parameters: dict  # JSON Schema dict


@dataclass
class LLMResponse:
    """
    Respuesta genérica de un LLM. Puede ser del tipo `texto` o una llamada a tool
    """

    type: Literal["text", "tool_calls"]
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
