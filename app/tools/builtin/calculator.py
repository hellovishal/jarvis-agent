
from pydantic import BaseModel, Field

from app.tools.base import BaseTool


class CalculatorInput(BaseModel):
    numbers: list[float] = Field(
        min_length=1,
        max_length=100,
        description="Numbers to add",
    )


class CalculatorTool(BaseTool):

    name = "sum_numbers"

    description = (
        "Calculate the sum of a list of numbers. "
        "Use this when the user asks to add numbers."
    )

    args_schema = CalculatorInput

    async def execute(
        self,
        arguments: CalculatorInput,
    ) -> dict:

        total = sum(arguments.numbers)

        return {
            "numbers": arguments.numbers,
            "result": total,
        }
