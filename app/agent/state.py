
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    MAX_ITERATIONS_REACHED = "max_iterations_reached"


@dataclass
class AgentState:
    messages: list[dict[str, Any]]
    status: AgentStatus = AgentStatus.IDLE
    iteration: int = 0
    max_iterations: int = 10

    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0

    executed_tools: list[dict] = field(default_factory=list)
    final_answer: str | None = None
    error: str | None = None
