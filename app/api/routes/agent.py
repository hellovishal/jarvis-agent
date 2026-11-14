
from fastapi import APIRouter, HTTPException, Request

from app.agent.schemas import AgentRequest, AgentResponse
from app.agent.state import AgentStatus

router = APIRouter(tags=["Agent"])


@router.post("/run", response_model=AgentResponse)
async def run_agent(
    payload: AgentRequest,
    request: Request,
):

    runtime = request.app.state.agent_runtime

    state = await runtime.run(payload.message)

    if state.status == AgentStatus.FAILED:
        raise HTTPException(
            status_code=502,
            detail="Agent execution failed",
        )

    return AgentResponse(
        status=state.status,
        answer=state.final_answer,
        iterations=state.iteration,
        tools_executed=state.executed_tools,
        prompt_tokens=state.total_prompt_tokens,
        completion_tokens=state.total_completion_tokens,
        error=state.error,
    )
