# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
from sqlalchemy.ext.asyncio import AsyncEngine

from logger import setup_logging
from api.v1.bot_config.view import router as bot_config_router
from DI.container import create_container
from database.database import InitDB


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
    app = FastAPI(
        title="Bot Config API",
        description="API for managing bot configurations",
        version="1.0.0",
        lifespan=lifespan,
    )

    container = create_container()
    setup_dishka(container, app)

    app.include_router(bot_config_router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    from src.config import settings

    uvicorn.run("main:app", host=settings.api.ip, port=settings.api.port, reload=True)
