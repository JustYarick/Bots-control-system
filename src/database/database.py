# database/database.py - оставьте только InitDB
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_utils import database_exists, create_database
from loguru import logger
from src.config import settings


class InitDB:
    def __init__(self):
        self.custom_create_database()

    def custom_create_database(self):
        url = settings.db.sync_url
        try:
            if not database_exists(url):
                create_database(url)
                logger.success("Database created!")
            else:
                logger.info("Database already exists.")
        except Exception as e:
            logger.error(f"Failed to create or check database: {e}")
            raise


class Base(DeclarativeBase):
    pass
