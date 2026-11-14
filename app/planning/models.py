from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class PlanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanTask(BaseModel):
    id: str
    title: str
    description: str
    dependencies: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str | None = None
    error: str | None = None
    attempts: int = 0


class ExecutionPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    goal: str
    tasks: list[PlanTask] = Field(min_length=1)
    status: PlanStatus = PlanStatus.PENDING