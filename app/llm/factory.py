
from openrouter import OpenRouter

from app.core.config import settings
from app.core.exceptions import ConfigurationError
from app.llm.base import BaseLLMProvider
from app.llm.openrouter import OpenRouterProvider


def create_llm_provider(client: OpenRouter) -> BaseLLMProvider:

    provider = settings.llm_provider.lower()

    if provider == "openrouter":
        return OpenRouterProvider(client)

    raise ConfigurationError(
        f"Unsupported LLM provider: {provider}"
    )
