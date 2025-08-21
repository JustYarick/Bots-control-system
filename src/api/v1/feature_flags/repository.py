from typing import Optional, List, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, exists, and_, desc
from sqlalchemy.orm import selectinload, joinedload

from database.models import (
    FeatureFlag,
    FeatureConfig,
    FeatureConfigFlag,
    FeatureConfigVersion,
    Environment,
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


class FeatureConfigVersionRepository(Protocol):
    """Интерфейс репозитория для версий конфигураций"""

    async def create_version(
        self, config_id: UUID, changelog: str = None, created_by: str = None
    ) -> FeatureConfigVersion: ...

    async def get_config_versions(self, config_id: UUID) -> List[FeatureConfigVersion]: ...

    async def get_latest_version(self, config_id: UUID) -> Optional[FeatureConfigVersion]: ...


class FeatureConfigVersionRepositoryImpl(FeatureConfigVersionRepository):
    """Репозиторий для версий конфигураций"""

    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def create_version(
        self, config_id: UUID, changelog: str = None, created_by: str = None
    ) -> FeatureConfigVersion:
        # Получаем последний номер версии
        latest_version = await self.get_latest_version(config_id)
        version_number = (latest_version.version_number + 1) if latest_version else 1

        version = FeatureConfigVersion(
            config_id=config_id,
            version_number=version_number,
            changelog=changelog,
            created_by=created_by,
        )
        self._session.add(version)
        await self._session.flush()
        await self._session.refresh(version)
        return version

    async def get_config_versions(self, config_id: UUID) -> List[FeatureConfigVersion]:
        query = (
            select(FeatureConfigVersion)
            .where(FeatureConfigVersion.config_id == config_id)
            .order_by(desc(FeatureConfigVersion.version_number))
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_latest_version(self, config_id: UUID) -> Optional[FeatureConfigVersion]:
        query = (
            select(FeatureConfigVersion)
            .where(FeatureConfigVersion.config_id == config_id)
            .order_by(desc(FeatureConfigVersion.version_number))
            .limit(1)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
