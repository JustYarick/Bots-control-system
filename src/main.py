import uvicorn

from src.logger import setup_logging
setup_logging()
from fastapi import FastAPI
from src.config import settings
from loguru import logger
from src.database.database import Database


db = Database()
db.init_engine()
app = FastAPI(title="FastAPI Example with DB + Alembic")

if __name__ == "__main__":
    try:
        uvicorn.run("app.main:app", host=settings.api.ip, port=settings.api.port, reload=True)
    except Exception as e:
        logger.error(f"Error starting server: {e}")