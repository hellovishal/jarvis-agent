
class ToolPermissionManager:

    def __init__(
        self,
        allowed_tools: set[str] | None = None,
    ):
        self.allowed_tools = allowed_tools or set()

    def is_allowed(self, tool_name: str) -> bool:
        return tool_name in self.allowed_tools

    def authorize(self, tool_name: str) -> None:
        if not self.is_allowed(tool_name):
            raise PermissionError(
                f"Tool execution not permitted: {tool_name}"
            )
