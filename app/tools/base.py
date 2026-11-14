
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseTool(ABC):
    """Base interface for all Jarvis tools."""

    name: str
    description: str
    args_schema: type[BaseModel]

    @abstractmethod
    async def execute(self, arguments: BaseModel) -> Any:
        """Execute the tool with validated arguments."""
        raise NotImplementedError

    def to_openrouter_schema(self) -> dict:
        """Convert tool metadata to OpenRouter function schema."""

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema(),
            },
        }
