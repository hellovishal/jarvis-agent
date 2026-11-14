from pathlib import Path

import aiosqlite

from app.core.config import settings


class Database:

    def __init__(self):
        self.db = None

    async def connect(self):

        db_path = Path(settings.database_url).resolve()

        # Create parent directory if it doesn't exist.
        db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.db = await aiosqlite.connect(
            str(db_path)
        )

        self.db.row_factory = aiosqlite.Row

        await self.db.execute(
            "PRAGMA foreign_keys = ON"
        )

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