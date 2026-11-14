
from pydantic import BaseModel, Field

from app.agent.state import AgentStatus


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)


class AgentResponse(BaseModel):
    status: AgentStatus
    answer: str | None
    iterations: int
    tools_executed: list[dict]
    prompt_tokens: int
    completion_tokens: int
    error: str | None = None
