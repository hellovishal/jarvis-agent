from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    goal: str = Field(
        min_length=1,
        max_length=10000,
        description="The goal Jarvis should plan and execute",
    )