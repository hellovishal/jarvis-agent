from app.memory.repository import MemoryRepository


class LongTermMemory:
    def __init__(
        self,
        repository: MemoryRepository,
        max_memories: int = 10,
    ):
        self.repository = repository
        self.max_memories = max_memories

    async def remember(
        self,
        user_id: str,
        content: str,
        category: str = "fact",
        importance: int = 3,
    ):
        if not content.strip():
            raise ValueError("Memory content cannot be empty")

        if not 1 <= importance <= 5:
            raise ValueError("Importance must be between 1 and 5")

        return await self.repository.save_memory(
            user_id=user_id,
            content=content.strip(),
            category=category,
            importance=importance,
        )

    async def recall(self, user_id: str) -> list[dict]:
        return await self.repository.get_memories(
            user_id,
            self.max_memories,
        )