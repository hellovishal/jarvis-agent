from app.memory.repository import MemoryRepository


class ShortTermMemory:
    def __init__(
        self,
        repository: MemoryRepository,
        max_messages: int = 20,
    ):
        self.repository = repository
        self.max_messages = max_messages

    async def create_conversation(self, user_id: str) -> str:
        return await self.repository.create_conversation(user_id)

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ):
        await self.repository.save_message(
            conversation_id,
            role,
            content,
        )

    async def get_context(self, conversation_id: str) -> list[dict]:
        return await self.repository.get_messages(
            conversation_id,
            self.max_messages,
        )