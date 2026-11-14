import pytest

from app.planning.planner import Planner


class FakeLLM:

    async def generate(self, messages, tools=None):

        class Response:
            content = """
            {
                "goal": "Create Java summary",
                "status": "pending",
                "tasks": [
                    {
                        "id": "task_1",
                        "title": "Research",
                        "description": "Research Java concurrency",
                        "dependencies": [],
                        "status": "pending"
                    },
                    {
                        "id": "task_2",
                        "title": "Summarize",
                        "description": "Summarize research",
                        "dependencies": ["task_1"],
                        "status": "pending"
                    }
                ]
            }
            """

        return Response()


@pytest.mark.asyncio
async def test_planner_creates_execution_plan():

    planner = Planner(FakeLLM())

    plan = await planner.create_plan(
        "Research Java concurrency and summarize it"
    )

    assert plan.goal == "Create Java summary"
    assert len(plan.tasks) == 2
    assert plan.tasks[1].dependencies == ["task_1"]


class InvalidLLM:

    async def generate(self, messages, tools=None):

        class Response:
            content = "This is not valid JSON"

        return Response()


@pytest.mark.asyncio
async def test_planner_rejects_invalid_json():

    planner = Planner(InvalidLLM())

    with pytest.raises(ValueError):
        await planner.create_plan("Create a summary")