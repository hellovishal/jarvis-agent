from app.memory.context_builder import MemoryContextBuilder
from app.memory.long_term import LongTermMemory
from app.memory.repository import MemoryRepository
from app.memory.short_term import ShortTermMemory


class MemoryManager:
    def __init__(self, repository: MemoryRepository):
        self.short_term = ShortTermMemory(repository)
        self.long_term = LongTermMemory(repository)
        self.context_builder = MemoryContextBuilder()

    async def create_conversation(self, user_id: str) -> str:
        return await self.short_term.create_conversation(user_id)

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ):
        await self.short_term.add_message(
            conversation_id,
            role,
            content,
        )

    async def remember(
        self,
        user_id: str,
        content: str,
        category: str = "fact",
        importance: int = 3,
    ):
        return await self.long_term.remember(
            user_id,
            content,
            category,
            importance,
        )

    async def recall(self, user_id: str) -> list[dict]:
        return await self.long_term.recall(user_id)

    async def build_context(
        self,
        user_id: str,
        conversation_id: str,
    ) -> list[dict]:

        messages = await self.short_term.get_context(
            conversation_id
        )

        memories = await self.long_term.recall(user_id)

        return self.context_builder.build(
            conversation_messages=messages,
            long_term_memories=memories,
        )