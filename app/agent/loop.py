
import json

from app.agent.state import AgentState, AgentStatus
from app.core.logger import logger


class AgentLoop:

    def __init__(self, llm, tool_registry, tool_executor):
        self.llm = llm
        self.tool_registry = tool_registry
        self.tool_executor = tool_executor

    async def run(self, state: AgentState) -> AgentState:

        state.status = AgentStatus.RUNNING

        try:
            while state.iteration < state.max_iterations:

                state.iteration += 1

                logger.info(
                    "agent_iteration_started",
                    iteration=state.iteration,
                )

                # 1. Get available tool schemas dynamically.
                available_tools = (
                    self.tool_registry.get_openrouter_schemas()
                )

                # 2. Ask LLM to decide the next action.
                result = await self.llm.generate(
                    messages=state.messages,
                    tools=available_tools,
                )

                state.total_prompt_tokens += result.prompt_tokens
                state.total_completion_tokens += (
                    result.completion_tokens
                )

                # 3. No tool call means the task is complete.
                if not result.tool_calls:

                    state.final_answer = result.content or ""
                    state.status = AgentStatus.COMPLETED

                    logger.info(
                        "agent_execution_completed",
                        iterations=state.iteration,
                    )

                    return state

                # 4. Preserve assistant tool-call message.
                state.messages.append({
                    "role": "assistant",
                    "content": result.content,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.name,
                                "arguments": json.dumps(
                                    call.arguments
                                ),
                            },
                        }
                        for call in result.tool_calls
                    ],
                })

                # 5. Execute requested tools.
                for call in result.tool_calls:

                    tool_result = await self.tool_executor.execute(
                        tool_name=call.name,
                        arguments=call.arguments,
                    )

                    state.executed_tools.append({
                        "name": call.name,
                        "arguments": call.arguments,
                        "success": tool_result.success,
                    })

                    # 6. Append structured observation.
                    state.messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(
                            tool_result.to_dict()
                        ),
                    })

                    logger.info(
                        "tool_execution_completed",
                        tool_name=call.name,
                        success=tool_result.success,
                    )

            state.status = AgentStatus.MAX_ITERATIONS_REACHED
            state.error = "Maximum agent iterations reached"

            return state

        except Exception as error:

            state.status = AgentStatus.FAILED
            state.error = "Agent execution failed"

            logger.exception(
                "agent_execution_failed",
                error_type=type(error).__name__,
            )

            return state
