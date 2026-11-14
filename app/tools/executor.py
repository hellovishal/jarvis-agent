
import asyncio

from pydantic import ValidationError

from app.core.logger import logger
from app.tools.permissions import ToolPermissionManager
from app.tools.registry import ToolRegistry
from app.tools.schemas import ToolResult


class ToolExecutor:

    def __init__(
        self,
        registry: ToolRegistry,
        permission_manager: ToolPermissionManager,
        timeout_seconds: int = 15,
    ):
        self.registry = registry
        self.permission_manager = permission_manager
        self.timeout_seconds = timeout_seconds

    async def execute(
        self,
        tool_name: str,
        arguments: dict,
    ) -> ToolResult:

        try:
            # 1. Find registered tool
            tool = self.registry.get(tool_name)

            # 2. Check permissions
            self.permission_manager.authorize(tool_name)

            # 3. Validate arguments
            validated_arguments = tool.args_schema.model_validate(
                arguments
            )

            # 4. Execute with timeout
            result = await asyncio.wait_for(
                tool.execute(validated_arguments),
                timeout=self.timeout_seconds,
            )

            return ToolResult(
                tool_name=tool_name,
                success=True,
                data=result,
            )

        except TimeoutError:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error="Tool execution timed out",
            )

        except (ValidationError, ValueError, TypeError, PermissionError) as error:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=str(error),
            )

        except Exception as error:  # noqa: BLE001
            logger.exception(
                "Unexpected tool execution failure",
                tool_name=tool_name,
                error_type=type(error).__name__,
            )

            return ToolResult(
                tool_name=tool_name,
                success=False,
                error="Unexpected tool execution error",
            )