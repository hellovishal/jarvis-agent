from uuid import uuid4

from app.core.database import Database


class MemoryRepository:
    def __init__(self, database: Database):
        self.database = database

    async def create_conversation(self, user_id: str) -> str:
        conversation_id = str(uuid4())

        await self.database.db.execute(
            """
            INSERT INTO conversations (id, user_id)
            VALUES (?, ?)
            """,
            (conversation_id, user_id),
        )
        await self.database.db.commit()

        return conversation_id

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ):
        message_id = str(uuid4())

        cursor = await self.database.db.execute(
            """
            INSERT INTO messages
                (id, conversation_id, role, content)
            SELECT ?, id, ?, ?
            FROM conversations
            WHERE id = ?
            """,
            (message_id, role, content, conversation_id),
        )

        if cursor.rowcount == 0:
            raise ValueError("Conversation not found")

        await self.database.db.execute(
            """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (conversation_id,),
        )

        await self.database.db.commit()

    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 20,
    ) -> list[dict]:
        cursor = await self.database.db.execute(
            """
            SELECT role, content
            FROM (
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at DESC, rowid DESC
                LIMIT ?
            )
            ORDER BY created_at ASC
            """,
            (conversation_id, limit),
        )

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def save_memory(
        self,
        user_id: str,
        content: str,
        category: str,
        importance: int = 3,
    ) -> str:
        memory_id = str(uuid4())

        await self.database.db.execute(
            """
            INSERT INTO memories
                (id, user_id, content, category, importance)
            VALUES (?, ?, ?, ?, ?)
            """,
            (memory_id, user_id, content, category, importance),
        )
        await self.database.db.commit()

        return memory_id

    async def get_memories(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[dict]:
        cursor = await self.database.db.execute(
            """
            SELECT id, content, category, importance
            FROM memories
            WHERE user_id = ?
            ORDER BY importance DESC, created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]