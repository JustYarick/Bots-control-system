from typing import Optional, List, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, exists

from database.models import (
    FeatureFlag,
)
from database.AbstractRepository import AbstractRepository
from exceptions.exceptions import FeatureFlagAlreadyExistsError, FeatureFlagNotFoundError


class FeatureFlagRepository(AbstractRepository[FeatureFlag], Protocol):
    """Интерфейс репозитория для FeatureFlag"""

    async def get_by_name(self, name: str) -> Optional[FeatureFlag]: ...


class FeatureFlagRepositoryImpl(FeatureFlagRepository):
    """Репозиторий для работы с функциями"""

    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def add(self, entity: FeatureFlag) -> FeatureFlag:
        existing = await self.get_by_name(entity.name)
        if existing:
            raise FeatureFlagAlreadyExistsError(
                f"Feature flag with name '{entity.name}' already exists"
            )

        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: UUID) -> Optional[FeatureFlag]:
        query = select(FeatureFlag).where(FeatureFlag.id == entity_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[FeatureFlag]:
        query = (
            select(FeatureFlag).offset(skip).limit(limit).order_by(FeatureFlag.updated_at.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(self, entity: FeatureFlag) -> FeatureFlag:
        existing = await self.get_by_id(entity.id)
        if not existing:
            raise FeatureFlagNotFoundError(f"Feature flag with id '{entity.id}' not found")

        await self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        query = delete(FeatureFlag).where(FeatureFlag.id == entity_id)
        result = await self._session.execute(query)
        return result.rowcount > 0

    async def exists(self, entity_id: UUID) -> bool:
        query = select(exists().where(FeatureFlag.id == entity_id))
        result = await self._session.execute(query)
        return result.scalar()

    async def get_by_name(self, name: str) -> Optional[FeatureFlag]:
        query = select(FeatureFlag).where(FeatureFlag.name == name)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
