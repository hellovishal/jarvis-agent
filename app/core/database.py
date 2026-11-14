from pathlib import Path

import aiosqlite

from app.core.config import settings


class Database:

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url
        self.db = None

    async def connect(self):
        database_url = self.database_url

        # Normalize SQLite URLs if provided.
        if database_url.startswith("sqlite+aiosqlite:///"):
            database_url = database_url.removeprefix(
                "sqlite+aiosqlite:///"
            )
        elif database_url.startswith("sqlite:///"):
            database_url = database_url.removeprefix("sqlite:///")

        db_path = Path(database_url).resolve()

        # Create parent directory if it doesn't exist.
        db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.db = await aiosqlite.connect(str(db_path))

        self.db.row_factory = aiosqlite.Row

        await self.db.execute("PRAGMA foreign_keys = ON")

        await self.initialize()

    async def initialize(self):

        await self.db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                importance INTEGER DEFAULT 3,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                goal TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS plan_tasks (
                plan_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                dependencies TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL,
                result TEXT,
                error TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (plan_id, task_id),

                FOREIGN KEY (plan_id)
                    REFERENCES plans(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_plans_user_id
            ON plans(user_id);

            CREATE INDEX IF NOT EXISTS idx_plan_tasks_status
            ON plan_tasks(plan_id, status);

            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id);

            CREATE INDEX IF NOT EXISTS idx_memories_user
            ON memories(user_id);
        """)

        await self.db.commit()

    async def close(self):

        if self.db:
            await self.db.close()
            self.db = None