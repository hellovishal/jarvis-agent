
import asyncio
import json
import httpx
from openrouter import OpenRouter

from app.core.config import settings
from app.core.exceptions import (
    ConfigurationError,
    LLMProviderError,
)
from app.core.logger import logger
from app.llm.base import BaseLLMProvider, LLMResult, ToolCall


class OpenRouterProvider(BaseLLMProvider):

    def __init__(self, client: OpenRouter):
        self.client = client

    @staticmethod
    def _is_retryable(error: Exception) -> bool:
        if isinstance(
            error,
            (httpx.TransportError, asyncio.TimeoutError),
        ):
            return True

        status_code = getattr(error, "status_code", None)

        if status_code is None:
            response = getattr(error, "response", None)
            status_code = getattr(response, "status_code", None)

        return status_code in {429, 500, 502, 503, 504}

    async def generate(self, messages, tools=None):

        request_args = {
            "model": settings.llm_model,
            "messages": messages,
            "stream": False,
        }

        if tools:
            request_args["tools"] = tools
            request_args["tool_choice"] = "auto"
            request_args["parallel_tool_calls"] = False

        response = await asyncio.wait_for(
            self.client.chat.send_async(**request_args),
            timeout=settings.llm_timeout_seconds,
        )

        return self.parse_openrouter_response(response)

    def parse_openrouter_response(self, response) -> LLMResult:
        choice = response.choices[0]
        message = choice.message

        tool_calls = []

        for call in (message.tool_calls or []):
            arguments = json.loads(call.function.arguments)

            tool_calls.append(
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=arguments,
                )
            )

        usage = response.usage

        return LLMResult(
            content=message.content,
            model=response.model,
            tool_calls=tool_calls,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0
        )
