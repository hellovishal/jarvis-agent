import json

from app.llm.base import BaseLLMProvider
from app.planning.graph import TaskGraph
from app.planning.models import ExecutionPlan


PLANNER_SYSTEM_PROMPT = """
You are the planning engine of Jarvis, an autonomous AI assistant.

Your responsibility is to decompose user goals into executable tasks.

Rules:
1. Break complex goals into small, actionable tasks.
2. Each task must have a clear title and description.
3. Identify dependencies between tasks.
4. Tasks without dependencies should have an empty dependencies list.
5. Use unique task IDs such as task_1, task_2.
6. Do not create unnecessary tasks.
7. Generate between 1 and 10 tasks.
8. Do not execute tasks.
9. Return ONLY valid JSON.

Required JSON structure:

{
    "goal": "User's goal",
    "status": "pending",
    "tasks": [
        {
            "id": "task_1",
            "title": "Task title",
            "description": "Detailed instructions",
            "dependencies": [],
            "status": "pending",
            "result": null,
            "error": null
        }
    ]
}
"""


class Planner:

    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def create_plan(self, user_goal: str) -> ExecutionPlan:

        messages = [
            {
                "role": "system",
                "content": PLANNER_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"Create an execution plan for this goal:\n"
                    f"{user_goal}"
                ),
            },
        ]

        response = await self.llm.generate(messages=messages)

        if not response.content:
            raise ValueError("Planner returned an empty response")

        plan_json = self._extract_json(response.content)

        plan = ExecutionPlan.model_validate_json(plan_json)

        # Validate dependencies and circular references.
        TaskGraph(plan)

        return plan

    @staticmethod
    def _extract_json(content: str) -> str:

        content = content.strip()

        # Handle markdown JSON code fences.
        if content.startswith("```"):
            lines = content.splitlines()

            if lines[-1].strip() == "```":
                lines = lines[1:-1]

            content = "\n".join(lines).strip()

        # Ensure the response contains valid JSON.
        json.loads(content)

        return content