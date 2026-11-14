from fastapi import APIRouter, HTTPException, Request
from app.core.logger import logger
from app.agent.schemas import AgentRequest, AgentResponse
from app.agent.state import AgentStatus

router = APIRouter(tags=["Agent"])


@router.post("/run", response_model=AgentResponse)
async def run_agent(
    payload: AgentRequest,
    request: Request,
):

    runtime = request.app.state.agent_runtime

    try:
        state, conversation_id = await runtime.run(
            user_message=payload.message,
            user_id=payload.user_id,
            conversation_id=payload.conversation_id,
        )

    except Exception as error:  # noqa: BLE001
        logger.exception(
            "Agent API request failed",
            error_type=type(error).__name__,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process agent request",
        ) from error

    if state.status == AgentStatus.FAILED:
        raise HTTPException(
            status_code=502,
            detail="Agent execution failed",
        )

    return AgentResponse(
        conversation_id=conversation_id,
        status=state.status,
        answer=state.final_answer,
        iterations=state.iteration,
        tools_executed=state.executed_tools,
        prompt_tokens=state.total_prompt_tokens,
        completion_tokens=state.total_completion_tokens,
        error=state.error,
    )