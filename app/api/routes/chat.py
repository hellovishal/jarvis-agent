
from fastapi import APIRouter, HTTPException, Request

from app.core.exceptions import (
    ConfigurationError,
    LLMProviderError,
)
from app.llm.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
):
    provider = request.app.state.llm_provider

    try:
        result = await provider.generate(
            [
                message.model_dump()
                for message in payload.messages
            ]
        )

        return ChatResponse(
            content=result.content,
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
        )

    except ConfigurationError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except LLMProviderError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
