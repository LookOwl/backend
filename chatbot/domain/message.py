from dataclasses import dataclass
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class ToolResult:
    tool_use_id: str
    content: str


@dataclass
class Message:
    role: MessageRole
    content: str | None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    tool_results: list[ToolResult] | None = None

    def to_dict(self) -> dict:
        d: dict = {"role": self.role.value, "content": self.content if self.content else ""}
        if self.tool_calls:
            d["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in self.tool_calls
            ]
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        if self.tool_results:
            d["tool_results"] = [
                {"tool_use_id": tr.tool_use_id, "content": tr.content}
                for tr in self.tool_results
            ]
        return d
