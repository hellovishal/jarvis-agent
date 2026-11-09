
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Jarvis Agent"
    app_env: str = "development"
    debug: bool = True

    llm_provider: str = "openrouter"
    llm_model: str = "google/gemini-2.5-flash"
    openrouter_api_key: str = ""

    database_url: str = "sqlite+aiosqlite:///./jarvis.db"

    max_agent_iterations: int = 10
    enable_tool_execution: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
