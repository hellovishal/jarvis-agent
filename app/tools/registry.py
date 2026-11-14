
from app.tools.base import BaseTool


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if not tool.name:
            raise ValueError("Tool name cannot be empty")

        if tool.name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool.name}"
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        tool = self._tools.get(name)

        if tool is None:
            raise ValueError(f"Unknown tool: {name}")

        return tool

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_openrouter_schemas(self) -> list[dict]:
        return [
            tool.to_openrouter_schema()
            for tool in self._tools.values()
        ]

    def has_tool(self, name: str) -> bool:
        return name in self._tools
