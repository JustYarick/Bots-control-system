# database/UnitOfWork.py
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        try:
            await self._session.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            logger.error(f"Commit failed: {e}")
            await self.rollback()
            raise

    async def rollback(self):
        try:
            await self._session.rollback()
            logger.debug("Transaction rolled back")
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise

    @property
    def session(self) -> AsyncSession:
        return self._session
