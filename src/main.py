# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
from sqlalchemy.ext.asyncio import AsyncEngine

from exceptions.exceptions import ApiError
from exceptions.exceptions_handler import setup_exception_handlers
from logger import setup_logging
from DI.container import create_container
from database.database import InitDB
from src.api import router as api_router
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация БД
    InitDB()
    yield

    # Правильное закрытие engine
    container = app.state.dishka_container
    if container:
        async with container() as request_container:
            try:
                engine = await request_container.get(AsyncEngine)
                await engine.dispose()
            except Exception as e:
                print(f"Error closing engine: {e}")


def create_app() -> FastAPI:
    setup_logging()
    logger.info("Creating FastAPI app")
    app = FastAPI(
        title="Bot Config API",
        description="API for managing bot configurations",
        version="1.0.0",
        lifespan=lifespan,
        responses={
            404: {"model": ApiError, "description": "Not Found"},
            409: {"model": ApiError, "description": "Conflict"},
            422: {"model": ApiError, "description": "Validation Error"},
            500: {"model": ApiError, "description": "Internal Server Error"},
        },
    )
    container = create_container()
    setup_dishka(container, app)
    setup_exception_handlers(app)
    app.include_router(api_router)

    return app


app = create_app()
