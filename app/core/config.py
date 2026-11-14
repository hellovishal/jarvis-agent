
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Jarvis Agent"
    app_env: str = "development"
    debug: bool = True

    llm_provider: str = "openrouter"
    llm_model: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    openrouter_api_key: str = ""
    workspace_dir: str = "./workspace"
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 3
    llm_retry_base_delay: float = 1.0
    max_conversation_messages: int = 20
    max_retrieved_memories: int = 10

    database_url: str = "./data/jarvis.db"

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
