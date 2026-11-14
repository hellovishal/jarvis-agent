from types import SimpleNamespace

import pytest
import asyncio
from app.agent.state import AgentStatus
from app.planning.executor import PlanExecutor
from app.planning.models import (
    ExecutionPlan,
    PlanStatus,
    PlanTask,
    TaskStatus,
)

class AlwaysFailAgentLoop:
    def __init__(self):
        self.calls = 0

    async def run(self, state):
        self.calls += 1

        return SimpleNamespace(
            status=AgentStatus.FAILED,
            final_answer=None,
            error="Permanent failure",
        )

class RetryFakeAgentLoop:
    def __init__(self):
        self.calls = 0

    async def run(self, state):
        self.calls += 1

        if self.calls < 3:
            return SimpleNamespace(
                status=AgentStatus.FAILED,
                final_answer=None,
                error="Temporary failure",
            )

        return SimpleNamespace(
            status=AgentStatus.COMPLETED,
            final_answer="Successfully completed",
            error=None,
        )

class FakeAgentLoop:

    def __init__(self, fail_first=False):
        self.calls = []
        self.fail_first = fail_first

    async def run(self, state):

        self.calls.append(state.messages)

        if self.fail_first and len(self.calls) == 1:
            return SimpleNamespace(
                status=AgentStatus.FAILED,
                final_answer=None,
                error="Simulated failure",
            )

        return SimpleNamespace(
            status=AgentStatus.COMPLETED,
            final_answer=f"Result {len(self.calls)}",
            error=None,
        )

class ParallelFakeAgentLoop:
    def __init__(self):
        self.active = 0
        self.max_active = 0
        self.calls = []

    async def run(self, state):
        self.active += 1
        self.max_active = max(self.max_active, self.active)

        self.calls.append(state.messages)

        try:
            await asyncio.sleep(0.1)

            return SimpleNamespace(
                status=AgentStatus.COMPLETED,
                final_answer=f"Result {len(self.calls)}",
                error=None,
            )
        finally:
            self.active -= 1

def create_plan():

    return ExecutionPlan(
        goal="Create Java concurrency summary",
        tasks=[
            PlanTask(
                id="task_1",
                title="Research",
                description="Research Java concurrency",
            ),
            PlanTask(
                id="task_2",
                title="Summarize",
                description="Summarize research",
                dependencies=["task_1"],
            ),
            PlanTask(
                id="task_3",
                title="Save",
                description="Save summary",
                dependencies=["task_2"],
            ),
        ],
    )


@pytest.mark.asyncio
async def test_plan_execution_success():

    plan = create_plan()

    fake_loop = FakeAgentLoop()

    executor = PlanExecutor(fake_loop)

    result = await executor.execute(plan)

    assert result.status == PlanStatus.COMPLETED

    assert all(
        task.status == TaskStatus.COMPLETED
        for task in result.tasks
    )

    assert len(fake_loop.calls) == 3


@pytest.mark.asyncio
async def test_dependent_task_receives_previous_result():

    plan = create_plan()

    fake_loop = FakeAgentLoop()

    executor = PlanExecutor(fake_loop)

    await executor.execute(plan)

    second_task_messages = fake_loop.calls[1]

    assert any(
        "Result 1" in message["content"]
        for message in second_task_messages
    )


@pytest.mark.asyncio
async def test_failed_task_blocks_dependent_tasks(monkeypatch):

    async def mock_sleep(delay):
        pass

    monkeypatch.setattr(
        "app.planning.executor.asyncio.sleep",
        mock_sleep,
    )

    plan = create_plan()

    fake_loop = AlwaysFailAgentLoop()

    executor = PlanExecutor(
        agent_loop=fake_loop,
        max_retries=2,
    )

    result = await executor.execute(plan)

    assert result.status == PlanStatus.FAILED

    assert result.tasks[0].status == TaskStatus.FAILED
    assert result.tasks[1].status == TaskStatus.BLOCKED
    assert result.tasks[2].status == TaskStatus.BLOCKED

    # Initial attempt + 2 retries
    assert fake_loop.calls == 3
    
@pytest.mark.asyncio
async def test_independent_tasks_execute_in_parallel():
    plan = ExecutionPlan(
        goal="Research Java concurrency",
        tasks=[
            PlanTask(
                id="task_1",
                title="Research Threads",
                description="Research Java threads",
            ),
            PlanTask(
                id="task_2",
                title="Research Locks",
                description="Research Java locks",
            ),
        ],
    )

    fake_loop = ParallelFakeAgentLoop()
    executor = PlanExecutor(fake_loop, max_concurrency=3)

    result = await executor.execute(plan)

    assert result.status == PlanStatus.COMPLETED
    assert fake_loop.max_active == 2
    assert len(fake_loop.calls) == 2


@pytest.mark.asyncio
async def test_concurrency_limit_is_respected():
    plan = ExecutionPlan(
        goal="Research Java concepts",
        tasks=[
            PlanTask(
                id=f"task_{i}",
                title=f"Task {i}",
                description=f"Research topic {i}",
            )
            for i in range(1, 5)
        ],
    )

    fake_loop = ParallelFakeAgentLoop()
    executor = PlanExecutor(fake_loop, max_concurrency=2)

    result = await executor.execute(plan)

    assert result.status == PlanStatus.COMPLETED
    assert fake_loop.max_active == 2
    
@pytest.mark.asyncio
async def test_failed_task_is_retried():
    plan = ExecutionPlan(
        goal="Test retry",
        tasks=[
            PlanTask(
                id="task_1",
                title="Test task",
                description="Execute test task",
            )
        ],
    )

    fake_loop = RetryFakeAgentLoop()

    executor = PlanExecutor(
        agent_loop=fake_loop,
        max_retries=2,
    )

    result = await executor.execute(plan)

    assert result.status == PlanStatus.COMPLETED
    assert result.tasks[0].status == TaskStatus.COMPLETED
    assert fake_loop.calls == 3