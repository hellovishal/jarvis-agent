
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str,Any]

@dataclass
class LLMResult:
    content: str
    model: str
    tool_calls:list[ToolCall] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class BaseLLMProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[dict] | None=None,
    ) -> LLMResult:
        """Generate a response from the supplied messages."""
        raise NotImplementedError
