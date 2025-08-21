from dishka import Provider, Scope, provide
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)

from src.config import DatabaseConfig, settings
from api.v1.feature_flags.repository import (
    FeatureFlagRepository,
    FeatureFlagRepositoryImpl,
    FeatureConfigRepository,
    FeatureConfigRepositoryImpl,
    FeatureConfigFlagRepository,
    FeatureConfigFlagRepositoryImpl,
    FeatureConfigVersionRepository,
    FeatureConfigVersionRepositoryImpl,
)
from api.v1.feature_flags.service import (
    FeatureFlagService,
    FeatureFlagServiceImpl,
    FeatureConfigService,
    FeatureConfigServiceImpl,
)
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
    def get_feature_flag_repository(self, session: AsyncSession) -> FeatureFlagRepository:
        return FeatureFlagRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_feature_config_repository(self, session: AsyncSession) -> FeatureConfigRepository:
        return FeatureConfigRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_feature_config_flag_repository(
        self, session: AsyncSession
    ) -> FeatureConfigFlagRepository:
        return FeatureConfigFlagRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_feature_config_version_repository(
        self, session: AsyncSession
    ) -> FeatureConfigVersionRepository:
        return FeatureConfigVersionRepositoryImpl(session)


class UnitOfWorkProvider(Provider):
    """Провайдер Unit of Work"""

    @provide(scope=Scope.REQUEST)
    def get_unit_of_work(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)


class ServiceProvider(Provider):
    """Провайдер сервисов"""

    @provide(scope=Scope.REQUEST)
    def get_feature_flag_service(
        self, repository: FeatureFlagRepository, uow: UnitOfWork
    ) -> FeatureFlagService:
        return FeatureFlagServiceImpl(repository, uow)

    @provide(scope=Scope.REQUEST)
    def get_feature_config_service(
        self,
        config_repository: FeatureConfigRepository,
        config_flag_repository: FeatureConfigFlagRepository,
        version_repository: FeatureConfigVersionRepository,
        uow: UnitOfWork,
    ) -> FeatureConfigService:
        return FeatureConfigServiceImpl(
            config_repository, config_flag_repository, version_repository, uow
        )
