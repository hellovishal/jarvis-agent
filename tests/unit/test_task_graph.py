import pytest

from app.planning.graph import TaskGraph
from app.planning.models import (
    ExecutionPlan,
    PlanTask,
    TaskStatus,
)


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


def test_topological_order():

    plan = create_plan()

    graph = TaskGraph(plan)

    ordered = graph.topological_order()

    assert [
        task.id for task in ordered
    ] == ["task_1", "task_2", "task_3"]


def test_ready_tasks():

    plan = create_plan()

    graph = TaskGraph(plan)

    ready = graph.get_ready_tasks()

    assert len(ready) == 1
    assert ready[0].id == "task_1"


def test_next_task_becomes_ready():

    plan = create_plan()

    graph = TaskGraph(plan)

    plan.tasks[0].status = TaskStatus.COMPLETED

    ready = graph.get_ready_tasks()

    assert ready[0].id == "task_2"


def test_circular_dependency():

    plan = ExecutionPlan(
        goal="Invalid plan",
        tasks=[
            PlanTask(
                id="task_1",
                title="Task 1",
                description="First task",
                dependencies=["task_2"],
            ),
            PlanTask(
                id="task_2",
                title="Task 2",
                description="Second task",
                dependencies=["task_1"],
            ),
        ],
    )

    with pytest.raises(ValueError):
        TaskGraph(plan)


def test_unknown_dependency():

    plan = ExecutionPlan(
        goal="Invalid plan",
        tasks=[
            PlanTask(
                id="task_1",
                title="Task 1",
                description="First task",
                dependencies=["unknown_task"],
            ),
        ],
    )

    with pytest.raises(ValueError):
        TaskGraph(plan)