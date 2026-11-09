
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.logger import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(
        "jarvis_starting",
        environment=settings.app_env,
    )

    yield

    logger.info("jarvis_shutting_down")


app = FastAPI(
    title=settings.app_name,
    description="A personal agentic AI assistant.",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Jarvis Agent",
        "version": "0.1.0",
        "status": "running",
    }
