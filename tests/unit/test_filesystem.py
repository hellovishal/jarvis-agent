
import pytest

from app.core.config import settings
from app.tools.builtin.filesystem import (
    ListFilesTool,
    ListFilesInput,
    ReadFileTool,
    ReadFileInput,
)


@pytest.mark.asyncio
async def test_read_file(tmp_path, monkeypatch):

    monkeypatch.setattr(
        settings,
        "workspace_dir",
        str(tmp_path),
    )

    sample = tmp_path / "hello.txt"
    sample.write_text("Hello Jarvis!", encoding="utf-8")

    tool = ReadFileTool()

    result = await tool.execute(
        ReadFileInput(path="hello.txt")
    )

    assert result["content"] == "Hello Jarvis!"


@pytest.mark.asyncio
async def test_list_files(tmp_path, monkeypatch):

    monkeypatch.setattr(
        settings,
        "workspace_dir",
        str(tmp_path),
    )

    (tmp_path / "hello.txt").write_text("Hello")
    (tmp_path / "docs").mkdir()

    tool = ListFilesTool()

    result = await tool.execute(
        ListFilesInput(directory=".")
    )

    assert len(result["entries"]) == 2


@pytest.mark.asyncio
async def test_path_traversal_blocked(tmp_path, monkeypatch):

    monkeypatch.setattr(
        settings,
        "workspace_dir",
        str(tmp_path),
    )

    tool = ReadFileTool()

    with pytest.raises(ValueError):
        await tool.execute(
            ReadFileInput(path="../outside.txt")
        )
