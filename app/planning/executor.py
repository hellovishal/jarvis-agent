import asyncio
import logging
from app.agent.loop import AgentLoop
from app.agent.state import AgentState, AgentStatus
from app.core.config import settings
from app.planning.context import PlannerContext
from app.planning.graph import TaskGraph
from app.planning.models import (
    ExecutionPlan,
    PlanStatus,
    PlanTask,
    TaskStatus,
)
logger = logging.getLogger(__name__)

class PlanExecutor:
    def __init__(
        self,
        agent_loop: AgentLoop,
        max_concurrency: int = 3,
        max_retries: int = 2,
    ):
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be at least 1")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        self.agent_loop = agent_loop
        self.max_concurrency = max_concurrency
        self.max_retries = max_retries

    async def execute(self, plan: ExecutionPlan) -> ExecutionPlan:
        graph = TaskGraph(plan)
        plan.status = PlanStatus.RUNNING

        pending = {task.id for task in plan.tasks}
        running: dict[asyncio.Task, PlanTask] = {}

        while pending or running:

            # 1. Block tasks whose dependencies have failed.
            for task in plan.tasks:
                if task.id not in pending:
                    continue

                dependency_statuses = [
                    graph.tasks[dep].status
                    for dep in task.dependencies
                ]

                if any(
                    status in (TaskStatus.FAILED, TaskStatus.BLOCKED)
                    for status in dependency_statuses
                ):
                    task.status = TaskStatus.BLOCKED
                    task.error = "One or more dependencies failed"
                    pending.remove(task.id)

            # 2. Find tasks whose dependencies are completed.
            available_slots = self.max_concurrency - len(running)

            ready_tasks = [
                task
                for task in graph.get_ready_tasks()
                if task.id in pending
            ]

            # 3. Schedule ready tasks concurrently.
            for task in ready_tasks[:available_slots]:
                task.status = TaskStatus.RUNNING
                pending.remove(task.id)

                future = asyncio.create_task(
                    self._execute_task(plan, task)
                )
                running[future] = task

            # 4. Wait until at least one task finishes.
            if running:
                completed, _ = await asyncio.wait(
                    running.keys(),
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for future in completed:
                    task = running.pop(future)
                    status, result, error = future.result()

                    task.status = status
                    task.result = result
                    task.error = error

            elif pending:
                # No runnable tasks remain. Mark remaining tasks blocked.
                for task in plan.tasks:
                    if task.id in pending:
                        task.status = TaskStatus.BLOCKED
                        task.error = "Dependencies could not be completed"

                pending.clear()

        all_completed = all(
            task.status == TaskStatus.COMPLETED
            for task in plan.tasks
        )

        plan.status = (
            PlanStatus.COMPLETED
            if all_completed
            else PlanStatus.FAILED
        )

        return plan

    async def _execute_task(
        self,
        plan: ExecutionPlan,
        task: PlanTask,
    ) -> tuple[TaskStatus, str | None, str | None]:

        for attempt in range(self.max_retries + 1):
            task.attempts = attempt+1
            try:
                messages = PlannerContext.build_task_messages(
                    plan=plan,
                    task=task,
                )

                state = AgentState(
                    messages=messages,
                    max_iterations=settings.max_agent_iterations,
                )

                state = await self.agent_loop.run(state)

                if (
                    state.status == AgentStatus.COMPLETED
                    and state.final_answer
                ):
                    return TaskStatus.COMPLETED, state.final_answer, None

                error = state.error or "Task execution failed"

            except Exception as error:  # noqa: BLE001
                logger.exception(
                    "Task execution raised an exception",
                    extra={
                        "task_id": task.id,
                        "attempt": attempt + 1,
                    },
                )
                error = str(error)

            if attempt < self.max_retries:
                delay = 2 ** attempt

                logger.warning(
                    "Retrying failed task",
                    extra={
                        "task_id": task.id,
                        "attempt": attempt + 1,
                        "retry_delay": delay,
                    },
                )

                await asyncio.sleep(delay)

        return TaskStatus.FAILED, None, error