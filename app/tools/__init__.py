
from app.tools.builtin import (
    CalculatorTool,
    ListFilesTool,
    ReadFileTool,
)
from app.tools.executor import ToolExecutor
from app.tools.permissions import ToolPermissionManager
from app.tools.registry import ToolRegistry


def create_tool_engine():

    registry = ToolRegistry()

    # Register built-in tools
    registry.register(CalculatorTool())
    registry.register(ListFilesTool())
    registry.register(ReadFileTool())

    # Define permitted tools
    permissions = ToolPermissionManager(
        allowed_tools={
            "sum_numbers",
            "list_files",
            "read_file",
        }
    )

    executor = ToolExecutor(
        registry=registry,
        permission_manager=permissions,
        timeout_seconds=15,
    )

    return registry, executor
