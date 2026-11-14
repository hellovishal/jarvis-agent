import pytest

from app.core.database import Database
from app.planning.models import (
    ExecutionPlan,
    PlanStatus,
    PlanTask,
    TaskStatus,
)
from app.planning.repository import PlanRepository


@pytest.fixture
async def plan_repository(tmp_path):
    db_path = tmp_path / "test_plans.db"

    database = Database(database_url=str(db_path))
    await database.connect()

    repository = PlanRepository(database)

    yield repository

    await database.close()


def create_test_plan():
    return ExecutionPlan(
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
                dependencies=["task_1"],
            ),
        ],
    )


@pytest.mark.asyncio
async def test_save_and_retrieve_plan(plan_repository):
    plan = create_test_plan()

    await plan_repository.save_plan(plan, user_id="user_1")

    result = await plan_repository.get_plan(
        plan_id=plan.id,
        user_id="user_1",
    )

    assert result is not None
    assert result.id == plan.id
    assert result.goal == plan.goal
    assert len(result.tasks) == 2
    assert result.tasks[1].dependencies == ["task_1"]


@pytest.mark.asyncio
async def test_plan_is_not_accessible_to_another_user(plan_repository):
    plan = create_test_plan()

    await plan_repository.save_plan(plan, user_id="user_1")

    result = await plan_repository.get_plan(
        plan_id=plan.id,
        user_id="user_2",
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_task_status(plan_repository):
    plan = create_test_plan()

    await plan_repository.save_plan(plan, user_id="user_1")

    task = plan.tasks[0]
    task.status = TaskStatus.COMPLETED
    task.result = "Threads research completed"
    task.attempts = 1

    await plan_repository.update_task(plan.id, task)

    result = await plan_repository.get_plan(plan.id, "user_1")

    assert result.tasks[0].status == TaskStatus.COMPLETED
    assert result.tasks[0].result == "Threads research completed"
    assert result.tasks[0].attempts == 1


@pytest.mark.asyncio
async def test_update_plan_status(plan_repository):
    plan = create_test_plan()

    await plan_repository.save_plan(plan, user_id="user_1")

    await plan_repository.update_plan_status(
        plan.id,
        PlanStatus.RUNNING,
    )

    result = await plan_repository.get_plan(plan.id, "user_1")

    assert result.status == PlanStatus.RUNNING


@pytest.mark.asyncio
async def test_get_recoverable_plans(plan_repository):
    plan = create_test_plan()

    await plan_repository.save_plan(plan, user_id="user_1")

    await plan_repository.update_plan_status(
        plan.id,
        PlanStatus.RUNNING,
    )

    results = await plan_repository.get_recoverable_plans("user_1")

    assert len(results) == 1
    assert results[0].id == plan.id