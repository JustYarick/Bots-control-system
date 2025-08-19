from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from loguru import logger
from src.config import settings


class Database:
    def __init__(self, db_url: str = settings.db.async_url):
        self.db_url = db_url
        self.engine = None
        self._sessionmaker = None

    def init_engine(self):
        if self.engine:
            return
        try:
            self.engine = create_async_engine(
                self.db_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            self._sessionmaker = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info(f"DB engine created for {self.db_url}")
        except Exception as e:
            logger.error(f"DB engine creation failed: {e}")
            raise

    async def get_session(self) -> AsyncSession:
        if not self._sessionmaker:
            raise RuntimeError("Engine is not initialized. Call init_engine() first.")

        logger.debug("Opening new DB session")
        async with self._sessionmaker() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"DB session error: {e}")
                raise
            finally:
                logger.debug("Closing DB session")
