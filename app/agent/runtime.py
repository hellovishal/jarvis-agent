
from app.agent.context import build_initial_messages
from app.agent.loop import AgentLoop
from app.agent.state import AgentState
from app.core.config import settings
from app.tools import create_tool_engine


class AgentRuntime:

    def __init__(self, llm):

        self.llm = llm

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

    async def run(self, user_message: str) -> AgentState:

        state = AgentState(
            messages=build_initial_messages(user_message),
            max_iterations=settings.max_agent_iterations,
        )

        return await self.agent_loop.run(state)
