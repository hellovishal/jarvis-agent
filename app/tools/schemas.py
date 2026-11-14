
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    data: Any = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }
