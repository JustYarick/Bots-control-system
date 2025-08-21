from typing import Optional, List, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, exists, and_
from sqlalchemy.orm import selectinload

from database.models import (
    FeatureConfig,
    FeatureConfigFlag,
    Environment,
)
from database.AbstractRepository import AbstractRepository
from exceptions.exceptions import FeatureFlagAlreadyExistsError, FeatureFlagNotFoundError


class FeatureConfigRepository(AbstractRepository[FeatureConfig], Protocol):
    """Интерфейс репозитория для FeatureConfig"""

    async def get_by_name_and_env(
        self, name: str, environment: Environment
    ) -> Optional[FeatureConfig]: ...

    async def get_by_environment(self, environment: Environment) -> List[FeatureConfig]: ...

    async def get_active_configs(self) -> List[FeatureConfig]: ...

    async def activate_config(self, config_id: UUID) -> bool: ...

    async def deactivate_config(self, config_id: UUID) -> bool: ...


class FeatureConfigRepositoryImpl(FeatureConfigRepository):
    """Репозиторий для работы с конфигурациями"""

    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def add(self, entity: FeatureConfig) -> FeatureConfig:
        existing = await self.get_by_name_and_env(entity.name, entity.environment)
        if existing:
            raise FeatureFlagAlreadyExistsError(
                f"Feature config with name '{entity.name}' in environment '{entity.environment}' already exists"
            )

        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: UUID) -> Optional[FeatureConfig]:
        query = (
            select(FeatureConfig)
            .options(
                selectinload(FeatureConfig.features).selectinload(FeatureConfigFlag.feature),
                selectinload(FeatureConfig.versions),
            )
            .where(FeatureConfig.id == entity_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[FeatureConfig]:
        query = (
            select(FeatureConfig)
            .options(selectinload(FeatureConfig.versions))
            .offset(skip)
            .limit(limit)
            .order_by(FeatureConfig.updated_at.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(self, entity: FeatureConfig) -> FeatureConfig:
        existing = await self.get_by_id(entity.id)
        if not existing:
            raise FeatureFlagNotFoundError(f"Feature config with id '{entity.id}' not found")

        await self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        query = delete(FeatureConfig).where(FeatureConfig.id == entity_id)
        result = await self._session.execute(query)
        return result.rowcount > 0

    async def exists(self, entity_id: UUID) -> bool:
        query = select(exists().where(FeatureConfig.id == entity_id))
        result = await self._session.execute(query)
        return result.scalar()

    async def get_by_name_and_env(
        self, name: str, environment: Environment
    ) -> Optional[FeatureConfig]:
        query = select(FeatureConfig).where(
            and_(FeatureConfig.name == name, FeatureConfig.environment == environment)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_environment(self, environment: Environment) -> List[FeatureConfig]:
        query = (
            select(FeatureConfig)
            .where(FeatureConfig.environment == environment)
            .order_by(FeatureConfig.updated_at.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_active_configs(self) -> List[FeatureConfig]:
        query = (
            select(FeatureConfig)
            .where(FeatureConfig.is_active == True)
            .order_by(FeatureConfig.updated_at.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def activate_config(self, config_id: UUID) -> bool:
        query = update(FeatureConfig).where(FeatureConfig.id == config_id).values(is_active=True)
        result = await self._session.execute(query)
        return result.rowcount > 0

    async def deactivate_config(self, config_id: UUID) -> bool:
        query = update(FeatureConfig).where(FeatureConfig.id == config_id).values(is_active=False)
        result = await self._session.execute(query)
        return result.rowcount > 0
