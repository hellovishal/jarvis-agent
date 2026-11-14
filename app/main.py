from contextlib import asynccontextmanager

from fastapi import FastAPI
from openrouter import OpenRouter

from app.agent.runtime import AgentRuntime
from app.api.routes.agent import router as agent_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.database import Database
from app.core.logger import logger, setup_logging
from app.llm.factory import create_llm_provider
from app.memory.manager import MemoryManager
from app.memory.repository import MemoryRepository


@asynccontextmanager
async def lifespan(app: FastAPI):

    setup_logging()

    logger.info(
        "jarvis_starting",
        environment=settings.app_env,
    )

    database = Database()

    try:
        async with OpenRouter(
            api_key=settings.openrouter_api_key,
            x_open_router_title=settings.app_name,
        ) as client:

            # 1. Initialize LLM provider.
            app.state.llm_provider = create_llm_provider(client)

            logger.info("llm_provider_initialized")

            # 2. Initialize database connection.
            await database.connect()

            # 3. Initialize memory components.
            repository = MemoryRepository(database)
            memory_manager = MemoryManager(repository)

            app.state.database = database
            app.state.memory_manager = memory_manager

            # 4. Initialize agent runtime.
            app.state.agent_runtime = AgentRuntime(
                llm=app.state.llm_provider,
                memory_manager=memory_manager,
            )

            logger.info("agent_runtime_initialized")

            # Application serves requests while resources remain open.
            yield

    finally:
        # 5. Close database only during application shutdown.
        await database.close()

        logger.info("jarvis_shutting_down")


app = FastAPI(
    title=settings.app_name,
    description="A personal agentic AI assistant.",
    version="0.2.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health_router)

app.include_router(
    chat_router,
    prefix="/api/v1",
)

app.include_router(
    agent_router,
    prefix="/api/v1/agent",
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Jarvis Agent",
        "version": "0.2.0",
        "status": "running",
    }