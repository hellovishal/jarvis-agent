from app.agent.loop import AgentLoop
from app.agent.state import AgentState, AgentStatus
from app.core.config import settings
from app.memory.manager import MemoryManager
from app.tools import create_tool_engine
from app.planning.executor import PlanExecutor
from app.planning.planner import Planner
from app.planning.models import ExecutionPlan

class AgentRuntime:

    def __init__(self, llm, memory_manager: MemoryManager):

        self.llm = llm
        self.memory_manager = memory_manager

        # Initialize Tool Engine.
        self.tool_registry, self.tool_executor = (
            create_tool_engine()
        )

        # Initialize Agent Loop.
        self.agent_loop = AgentLoop(
            llm=self.llm,
            tool_registry=self.tool_registry,
            tool_executor=self.tool_executor,
        )
        
        self.planner = Planner(self.llm)
        self.plan_executor = PlanExecutor(self.agent_loop)

    async def run(
        self,
        user_message: str,
        user_id: str = "local-user",
        conversation_id: str | None = None,
    ) -> tuple[AgentState, str]:

        # 1. Create or reuse conversation.
        if conversation_id is None:
            conversation_id = (
                await self.memory_manager.create_conversation(user_id)
            )

        # 2. Persist incoming user message.
        await self.memory_manager.save_message(
            conversation_id,
            "user",
            user_message,
        )

        # 3. Retrieve conversation history + long-term memories.
        messages = await self.memory_manager.build_context(
            user_id=user_id,
            conversation_id=conversation_id,
        )

        # 4. Initialize Agent State using memory context.
        state = AgentState(
            messages=messages,
            max_iterations=settings.max_agent_iterations,
        )

        # 5. Execute Agent Loop.
        state = await self.agent_loop.run(state)

        # 6. Persist assistant response.
        if state.status == AgentStatus.COMPLETED and state.final_answer:
            await self.memory_manager.save_message(
                conversation_id,
                "assistant",
                state.final_answer,
            )

        return state, conversation_id
    
    async def run_plan(self, user_goal: str) -> ExecutionPlan:
        plan = await self.planner.create_plan(user_goal)
        return await self.plan_executor.execute(plan)