from typing import Optional, List, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload, joinedload

from database.models import (
    FeatureConfigFlag,
)
from exceptions.exceptions import FeatureFlagAlreadyExistsError


class FeatureConfigFlagRepository(Protocol):
    """Интерфейс репозитория для связи конфигурации и функций"""

    async def add_feature_to_config(
        self, config_id: UUID, feature_id: UUID, **kwargs
    ) -> FeatureConfigFlag: ...

    async def remove_feature_from_config(self, config_id: UUID, feature_id: UUID) -> bool: ...

    async def update_config_feature(
        self, config_id: UUID, feature_id: UUID, **kwargs
    ) -> Optional[FeatureConfigFlag]: ...

    async def get_config_features(self, config_id: UUID) -> List[FeatureConfigFlag]: ...

    async def get_config_feature(
        self, config_id: UUID, feature_id: UUID
    ) -> Optional[FeatureConfigFlag]: ...


class FeatureConfigFlagRepositoryImpl(FeatureConfigFlagRepository):
    """Репозиторий для связей конфигурации и функций"""

    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def add_feature_to_config(
        self, config_id: UUID, feature_id: UUID, **kwargs
    ) -> FeatureConfigFlag:
        existing = await self.get_config_feature(config_id, feature_id)
        if existing:
            raise FeatureFlagAlreadyExistsError("Feature already exists in this config")

        config_feature = FeatureConfigFlag(
            config_id=config_id,
            feature_id=feature_id,
            is_enabled=kwargs.get("is_enabled", False),
            is_free=kwargs.get("is_free", False),
            disabled_message=kwargs.get("disabled_message", None),
        )

        self._session.add(config_feature)
        await self._session.flush()
        await self._session.refresh(config_feature, ["feature"])
        return config_feature

    async def get_config_features(self, config_id: UUID) -> List[FeatureConfigFlag]:
        query = (
            select(FeatureConfigFlag)
            .options(joinedload(FeatureConfigFlag.feature))
            .where(FeatureConfigFlag.config_id == config_id)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def remove_feature_from_config(self, config_id: UUID, feature_id: UUID) -> bool:
        query = delete(FeatureConfigFlag).where(
            and_(
                FeatureConfigFlag.config_id == config_id, FeatureConfigFlag.feature_id == feature_id
            )
        )
        result = await self._session.execute(query)
        return result.rowcount > 0

    async def update_config_feature(
        self, config_id: UUID, feature_id: UUID, **kwargs
    ) -> Optional[FeatureConfigFlag]:
        query = (
            update(FeatureConfigFlag)
            .where(
                and_(
                    FeatureConfigFlag.config_id == config_id,
                    FeatureConfigFlag.feature_id == feature_id,
                )
            )
            .values(**kwargs)
            .returning(FeatureConfigFlag)
        )
        result = await self._session.execute(query)
        updated = result.scalar_one_or_none()
        if updated:
            await self._session.refresh(updated)
        return updated

    async def get_config_features(self, config_id: UUID) -> List[FeatureConfigFlag]:
        query = (
            select(FeatureConfigFlag)
            .options(selectinload(FeatureConfigFlag.feature))
            .where(FeatureConfigFlag.config_id == config_id)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_config_feature(
        self, config_id: UUID, feature_id: UUID
    ) -> Optional[FeatureConfigFlag]:
        query = (
            select(FeatureConfigFlag)
            .options(selectinload(FeatureConfigFlag.feature))
            .where(
                and_(
                    FeatureConfigFlag.config_id == config_id,
                    FeatureConfigFlag.feature_id == feature_id,
                )
            )
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
