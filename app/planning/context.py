from app.planning.models import ExecutionPlan, PlanTask


class PlannerContext:

    @staticmethod
    def build_task_messages(
        plan: ExecutionPlan,
        task: PlanTask,
    ) -> list[dict]:

        completed_results = []

        for dependency_id in task.dependencies:

            dependency = next(
                item
                for item in plan.tasks
                if item.id == dependency_id
            )

            completed_results.append(
                {
                    "task_id": dependency.id,
                    "title": dependency.title,
                    "result": dependency.result,
                }
            )

        return [
            {
                "role": "system",
                "content": (
                    "You are Jarvis, an AI assistant executing "
                    "one task from a larger execution plan. "
                    "Complete only the assigned task. "
                    "Use dependency results when provided. "
                    "Do not claim an action succeeded unless "
                    "you have actually completed it."
                ),
            },
            {
                "role": "user",
                "content": f"""
Overall Goal:
{plan.goal}

Current Task:
{task.title}

Task Instructions:
{task.description}

Previous Task Results:
{completed_results}

Execute the current task and provide its result.
""",
            },
        ]