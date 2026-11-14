import asyncio
import json

from app.core.database import Database
from app.planning.models import (
    ExecutionPlan,
    PlanStatus,
    PlanTask,
    TaskStatus,
)


class PlanRepository:
    def __init__(self, database: Database):
        self.db = database.db
        self._lock = asyncio.Lock()

    async def save_plan(
        self,
        plan: ExecutionPlan,
        user_id: str,
    ) -> None:
        async with self._lock:
            try:
                await self.db.execute("BEGIN")

                await self.db.execute(
                    """
                    INSERT INTO plans (id, user_id, goal, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        plan.id,
                        user_id,
                        plan.goal,
                        plan.status.value,
                    ),
                )

                for task in plan.tasks:
                    await self.db.execute(
                        """
                        INSERT INTO plan_tasks (
                            plan_id,
                            task_id,
                            title,
                            description,
                            dependencies,
                            status,
                            result,
                            error,
                            attempts
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            plan.id,
                            task.id,
                            task.title,
                            task.description,
                            json.dumps(task.dependencies),
                            task.status.value,
                            task.result,
                            task.error,
                            task.attempts,
                        ),
                    )

                await self.db.commit()

            except Exception:
                await self.db.rollback()
                raise

    async def update_plan_status(
        self,
        plan_id: str,
        status: PlanStatus,
    ) -> None:
        async with self._lock:
            await self.db.execute(
                """
                UPDATE plans
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status.value, plan_id),
            )
            await self.db.commit()

    async def update_task(
        self,
        plan_id: str,
        task: PlanTask,
    ) -> None:
        async with self._lock:
            await self.db.execute(
                """
                UPDATE plan_tasks
                SET status = ?,
                    result = ?,
                    error = ?,
                    attempts = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE plan_id = ? AND task_id = ?
                """,
                (
                    task.status.value,
                    task.result,
                    task.error,
                    task.attempts,
                    plan_id,
                    task.id,
                ),
            )
            await self.db.commit()

    async def get_plan(
        self,
        plan_id: str,
        user_id: str,
    ) -> ExecutionPlan | None:
        async with self._lock:
            cursor = await self.db.execute(
                """
                SELECT id, goal, status
                FROM plans
                WHERE id = ? AND user_id = ?
                """,
                (plan_id, user_id),
            )
            plan_row = await cursor.fetchone()

            if plan_row is None:
                return None

            cursor = await self.db.execute(
                """
                SELECT task_id, title, description,
                       dependencies, status, result,
                       error, attempts
                FROM plan_tasks
                WHERE plan_id = ?
                ORDER BY rowid
                """,
                (plan_id,),
            )
            task_rows = await cursor.fetchall()

        tasks = [
            PlanTask(
                id=row[0],
                title=row[1],
                description=row[2],
                dependencies=json.loads(row[3]),
                status=TaskStatus(row[4]),
                result=row[5],
                error=row[6],
                attempts=row[7],
            )
            for row in task_rows
        ]

        return ExecutionPlan(
            id=plan_row[0],
            goal=plan_row[1],
            status=PlanStatus(plan_row[2]),
            tasks=tasks,
        )

    async def get_recoverable_plans(
        self,
        user_id: str,
    ) -> list[ExecutionPlan]:
        async with self._lock:
            cursor = await self.db.execute(
                """
                SELECT id
                FROM plans
                WHERE user_id = ?
                  AND status IN (?, ?)
                ORDER BY created_at
                """,
                (
                    user_id,
                    PlanStatus.PENDING.value,
                    PlanStatus.RUNNING.value,
                ),
            )
            rows = await cursor.fetchall()

        plans = []

        for row in rows:
            plan = await self.get_plan(
                plan_id=row[0],
                user_id=user_id,
            )
            if plan is not None:
                plans.append(plan)

        return plans