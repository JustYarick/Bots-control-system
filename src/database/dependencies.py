from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.UnitOfWork import UnitOfWork
from database.database import get_db_session


async def get_uow() -> UnitOfWork:
    """Dependency для Unit of Work (для случаев когда нужна одна транзакция)"""
    uow = UnitOfWork()
    try:
        yield uow
    finally:
        if uow._should_close_session:
            await uow._session.close()


def get_uow_with_session(session: AsyncSession = Depends(get_db_session)) -> UnitOfWork:
    """Dependency для Unit of Work с переданной сессией (рекомендуется)"""
    return UnitOfWork(session)
