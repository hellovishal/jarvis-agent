import pytest

from app.core.database import Database
from app.memory.manager import MemoryManager
from app.memory.repository import MemoryRepository


@pytest.mark.asyncio
async def test_memory_manager(tmp_path, monkeypatch):
    from app.core import database as database_module

    # Use a temporary database for testing.
    db = Database()
    db.db = await database_module.aiosqlite.connect(
        str(tmp_path / "test.db")
    )
    db.db.row_factory = database_module.aiosqlite.Row
    await db.initialize()

    repository = MemoryRepository(db)
    manager = MemoryManager(repository)

    conversation_id = await manager.create_conversation("user_1")

    await manager.save_message(
        conversation_id,
        "user",
        "My name is Alex",
    )

    await manager.remember(
        "user_1",
        "Prefers concise answers",
        category="preference",
        importance=5,
    )

    context = await manager.build_context(
        "user_1",
        conversation_id,
    )

    assert len(context) == 2
    assert context[0]["role"] == "system"
    assert "Prefers concise answers" in context[0]["content"]
    assert context[1]["content"] == "My name is Alex"

    await db.close()