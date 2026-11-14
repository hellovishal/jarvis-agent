from fastapi import APIRouter, HTTPException, Request
from app.core.logger import logger
from app.agent.schemas import AgentRequest, AgentResponse
from app.agent.state import AgentStatus
from app.planning.models import ExecutionPlan
from app.planning.schemas import PlanRequest

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
    
    
    
@router.post("/plan", response_model=ExecutionPlan)
async def execute_plan(
    request: Request,
    payload: PlanRequest,
):
    try:
        runtime = request.app.state.agent_runtime

        plan = await runtime.run_plan(payload.goal)

        return plan

    except ValueError as error:
        logger.warning(
            "Plan creation failed",
            error=str(error),
        )
        raise HTTPException(
            status_code=422,
            detail="Unable to create a valid execution plan",
        ) from error

    except Exception as error:  # noqa: BLE001
        logger.exception(
            "Plan execution failed",
            error_type=type(error).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail="Plan execution failed",
        ) from error