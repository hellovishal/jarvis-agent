from app.planning.models import (
    ExecutionPlan,
    PlanTask,
    TaskStatus,
)


class TaskGraph:

    def __init__(self, plan: ExecutionPlan):
        self.plan = plan
        self.tasks = {
            task.id: task
            for task in plan.tasks
        }

        self.validate()

    def validate(self):
        task_ids = [task.id for task in self.plan.tasks]

        # Check duplicate task IDs.
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Duplicate task IDs found")

        # Check dependencies.
        for task in self.plan.tasks:

            for dependency in task.dependencies:

                if dependency == task.id:
                    raise ValueError(
                        f"Task cannot depend on itself: {task.id}"
                    )

                if dependency not in self.tasks:
                    raise ValueError(
                        f"Unknown dependency: {dependency}"
                    )

        # Detect circular dependencies.
        self.topological_order()

    def topological_order(self) -> list[PlanTask]:

        indegree = {
            task.id: len(task.dependencies)
            for task in self.plan.tasks
        }

        queue = [
            task_id
            for task_id, degree in indegree.items()
            if degree == 0
        ]

        ordered_tasks = []

        while queue:

            task_id = queue.pop(0)

            ordered_tasks.append(
                self.tasks[task_id]
            )

            for task in self.plan.tasks:

                if task_id in task.dependencies:

                    indegree[task.id] -= 1

                    if indegree[task.id] == 0:
                        queue.append(task.id)

        if len(ordered_tasks) != len(self.tasks):
            raise ValueError(
                "Circular dependency detected in task graph"
            )

        return ordered_tasks

    def get_ready_tasks(self) -> list[PlanTask]:

        ready_tasks = []

        for task in self.plan.tasks:

            if task.status != TaskStatus.PENDING:
                continue

            dependencies_completed = all(
                self.tasks[dependency].status
                == TaskStatus.COMPLETED
                for dependency in task.dependencies
            )

            if dependencies_completed:
                ready_tasks.append(task)

        return ready_tasks