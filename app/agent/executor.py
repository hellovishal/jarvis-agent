
# import asyncio
from typing import Any, Protocol


class ToolExecutor(Protocol):

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        ...


class DemoToolExecutor:

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:

        if name == "sum_numbers":
            numbers = arguments.get("numbers")

            if (
                not isinstance(numbers, list)
                or not numbers
                or len(numbers) > 100
                or any(
                    isinstance(n, bool)
                    or not isinstance(n, (int, float))
                    for n in numbers
                )
            ):
                raise ValueError("Invalid numbers argument")

            return {
                "result": sum(numbers)
            }

        raise ValueError(f"Unknown tool: {name}")


class AsyncToolExecutor:

    def __init__(self, executor):
        self.executor = executor

    async def execute(self, name, arguments):
        return await self.executor.execute(name, arguments)
