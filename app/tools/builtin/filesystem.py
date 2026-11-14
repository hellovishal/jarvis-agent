
from pathlib import Path

from pydantic import BaseModel, Field

from app.core.config import settings
from app.tools.base import BaseTool

MAX_FILE_SIZE = 1024 * 1024


def resolve_workspace_path(relative_path: str) -> Path:

    root = Path(settings.workspace_dir).resolve()

    candidate = (root / relative_path).resolve()

    if not candidate.is_relative_to(root):
        raise ValueError("Access outside workspace is forbidden")

    return candidate


class ListFilesInput(BaseModel):
    directory: str = Field(
        default=".",
        description="Relative directory inside Jarvis workspace",
    )


class ReadFileInput(BaseModel):
    path: str = Field(
        min_length=1,
        description="Relative file path inside Jarvis workspace",
    )


class ListFilesTool(BaseTool):

    name = "list_files"

    description = (
        "List files and directories inside the Jarvis workspace."
    )

    args_schema = ListFilesInput

    async def execute(self, arguments: ListFilesInput):

        directory = resolve_workspace_path(
            arguments.directory
        )

        if not directory.is_dir():
            raise ValueError("Directory does not exist")

        return {
            "directory": arguments.directory,
            "entries": [
                {
                    "name": item.name,
                    "type": (
                        "directory" if item.is_dir() else "file"
                    ),
                }
                for item in sorted(
                    directory.iterdir(),
                    key=lambda item: item.name.lower(),
                )[:100]
            ],
        }


class ReadFileTool(BaseTool):

    name = "read_file"

    description = (
        "Read a text file from the Jarvis workspace. "
        "Only files inside the workspace are accessible."
    )

    args_schema = ReadFileInput

    async def execute(self, arguments: ReadFileInput):

        file_path = resolve_workspace_path(
            arguments.path
        )

        if not file_path.is_file():
            raise ValueError("File does not exist")

        if file_path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError("File exceeds 1 MB limit")

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(
                "Only UTF-8 text files are supported"
            ) from error

        return {
            "path": arguments.path,
            "content": content,
        }
