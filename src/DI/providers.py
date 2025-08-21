# DI/providers.py
from dishka import Provider, Scope, provide
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)

from src.config import DatabaseConfig, settings
from api.v1.bot_config.repository import BotConfigRepository, BotConfigRepositoryImpl
from api.v1.bot_config.service import BotConfigService, BotConfigServiceImpl
from database.UnitOfWork import UnitOfWork


class DatabaseProvider(Provider):
    """Провайдер для работы с БД"""

    @provide(scope=Scope.APP)
    def get_database_config(self) -> DatabaseConfig:
        return settings.db

    @provide(scope=Scope.APP)
    def get_async_engine(self, db_config: DatabaseConfig) -> AsyncEngine:
        return create_async_engine(
            db_config.async_url, echo=False, pool_pre_ping=True, pool_size=10, max_overflow=20
        )

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


class RepositoryProvider(Provider):
    """Провайдер репозиториев"""

    @provide(scope=Scope.REQUEST)
    def get_bot_config_repository(self, session: AsyncSession) -> BotConfigRepository:
        return BotConfigRepositoryImpl(session)


class UnitOfWorkProvider(Provider):
    """Провайдер Unit of Work"""

    @provide(scope=Scope.REQUEST)
    def get_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)


class ServiceProvider(Provider):
    """Провайдер сервисов"""

    @provide(scope=Scope.REQUEST)
    def get_bot_config_service(
        self, repository: BotConfigRepository, uow: UnitOfWork
    ) -> BotConfigService:
        return BotConfigServiceImpl(repository, uow)
