from typing import Protocol, List, Optional
from uuid import UUID

from api.v1.feature_flags.schemas import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureConfigCreate,
    FeatureConfigUpdate,
    FeatureConfigFlagCreate,
    FeatureConfigFlagUpdate,
    FeatureConfigVersionCreate,
    Environment,
)
from database.UnitOfWork import UnitOfWork
from database.models import FeatureFlag, FeatureConfig, FeatureConfigFlag, FeatureConfigVersion
from .repository import (
    FeatureFlagRepository,
    FeatureConfigRepository,
    FeatureConfigFlagRepository,
    FeatureConfigVersionRepository,
)


class FeatureFlagService(Protocol):
    """Протокол сервиса для работы с функциями"""

    async def create_feature(self, feature_data: FeatureFlagCreate) -> FeatureFlag: ...

    async def list_features(self, skip: int = 0, limit: int = 100) -> List[FeatureFlag]: ...

    async def get_feature(self, feature_id: UUID) -> Optional[FeatureFlag]: ...

    async def get_feature_by_name(self, name: str) -> Optional[FeatureFlag]: ...

    async def update_feature(
        self, feature_id: UUID, update_data: FeatureFlagUpdate
    ) -> Optional[FeatureFlag]: ...

    async def delete_feature(self, feature_id: UUID) -> bool: ...


class FeatureConfigService(Protocol):
    """Протокол сервиса для работы с конфигурациями"""

    async def create_config(self, config_data: FeatureConfigCreate) -> FeatureConfig: ...

    async def list_configs(self, skip: int = 0, limit: int = 100) -> List[FeatureConfig]: ...

    async def get_config(self, config_id: UUID) -> Optional[FeatureConfig]: ...

    async def update_config(
        self, config_id: UUID, update_data: FeatureConfigUpdate
    ) -> Optional[FeatureConfig]: ...

    async def delete_config(self, config_id: UUID) -> bool: ...

    async def get_configs_by_environment(self, environment: Environment) -> List[FeatureConfig]: ...

    async def get_active_configs(self) -> List[FeatureConfig]: ...

    async def activate_config(self, config_id: UUID) -> bool: ...

    async def deactivate_config(self, config_id: UUID) -> bool: ...

    # Feature management
    async def add_feature_to_config(
        self, config_id: UUID, feature_data: FeatureConfigFlagCreate
    ) -> FeatureConfig: ...

    async def remove_feature_from_config(self, config_id: UUID, feature_id: UUID) -> bool: ...

    async def update_config_feature(
        self, config_id: UUID, feature_id: UUID, update_data: FeatureConfigFlagUpdate
    ) -> Optional[FeatureConfigFlag]: ...

    async def get_config_features(self, config_id: UUID) -> List[FeatureConfigFlag]: ...

    # Version management
    async def create_config_version(
        self, config_id: UUID, version_data: FeatureConfigVersionCreate
    ) -> FeatureConfigVersion: ...

    async def get_config_versions(self, config_id: UUID) -> List[FeatureConfigVersion]: ...


class FeatureFlagServiceImpl:
    """Сервис для работы с функциями"""

    def __init__(self, repository: FeatureFlagRepository, uow: UnitOfWork):
        self._repository = repository
        self._uow = uow

    async def create_feature(self, feature_data: FeatureFlagCreate) -> FeatureFlag:
        async with self._uow:
            feature = FeatureFlag(**feature_data.model_dump())
            return await self._repository.add(feature)

    async def list_features(self, skip: int = 0, limit: int = 100) -> List[FeatureFlag]:
        async with self._uow:
            return await self._repository.get_all(skip=skip, limit=limit)

    async def get_feature(self, feature_id: UUID) -> Optional[FeatureFlag]:
        async with self._uow:
            return await self._repository.get_by_id(feature_id)

    async def get_feature_by_name(self, name: str) -> Optional[FeatureFlag]:
        async with self._uow:
            return await self._repository.get_by_name(name)

    async def update_feature(
        self, feature_id: UUID, update_data: FeatureFlagUpdate
    ) -> Optional[FeatureFlag]:
        async with self._uow:
            feature = await self._repository.get_by_id(feature_id)
            if not feature:
                return None

            update_fields = update_data.model_dump(exclude_unset=True)
            for field, value in update_fields.items():
                setattr(feature, field, value)

            return await self._repository.update(feature)

    async def delete_feature(self, feature_id: UUID) -> bool:
        async with self._uow:
            return await self._repository.delete(feature_id)


class FeatureConfigServiceImpl:
    """Сервис для работы с конфигурациями"""

    def __init__(
        self,
        config_repository: FeatureConfigRepository,
        config_flag_repository: FeatureConfigFlagRepository,
        version_repository: FeatureConfigVersionRepository,
        uow: UnitOfWork,
    ):
        self._config_repository = config_repository
        self._config_flag_repository = config_flag_repository
        self._version_repository = version_repository
        self._uow = uow

    async def create_config(self, config_data: FeatureConfigCreate) -> FeatureConfig:
        async with self._uow:
            config = FeatureConfig(**config_data.model_dump())
            created_config = await self._config_repository.add(config)

            # Создаем первую версию
            await self._version_repository.create_version(
                config_id=created_config.id, changelog="Initial version"
            )

            return created_config

    async def list_configs(self, skip: int = 0, limit: int = 100) -> List[FeatureConfig]:
        async with self._uow:
            return await self._config_repository.get_all(skip=skip, limit=limit)

    async def get_config(self, config_id: UUID) -> Optional[FeatureConfig]:
        async with self._uow:
            return await self._config_repository.get_by_id(config_id)

    async def update_config(
        self, config_id: UUID, update_data: FeatureConfigUpdate
    ) -> Optional[FeatureConfig]:
        async with self._uow:
            config = await self._config_repository.get_by_id(config_id)
            if not config:
                return None

            update_fields = update_data.model_dump(exclude_unset=True)
            for field, value in update_fields.items():
                setattr(config, field, value)

            updated_config = await self._config_repository.update(config)

            # Создаем новую версию при обновлении
            await self._version_repository.create_version(
                config_id=config_id, changelog="Configuration updated"
            )

            return updated_config

    async def delete_config(self, config_id: UUID) -> bool:
        async with self._uow:
            return await self._config_repository.delete(config_id)

    async def get_configs_by_environment(self, environment: Environment) -> List[FeatureConfig]:
        async with self._uow:
            return await self._config_repository.get_by_environment(environment)

    async def get_active_configs(self) -> List[FeatureConfig]:
        async with self._uow:
            return await self._config_repository.get_active_configs()

    async def activate_config(self, config_id: UUID) -> bool:
        async with self._uow:
            success = await self._config_repository.activate_config(config_id)
            if success:
                await self._version_repository.create_version(
                    config_id=config_id, changelog="Configuration activated"
                )
            return success

    async def deactivate_config(self, config_id: UUID) -> bool:
        async with self._uow:
            success = await self._config_repository.deactivate_config(config_id)
            if success:
                await self._version_repository.create_version(
                    config_id=config_id, changelog="Configuration deactivated"
                )
            return success

    async def add_feature_to_config(
        self, config_id: UUID, feature_data: FeatureConfigFlagCreate
    ) -> FeatureConfig:
        """Добавить функцию в конфигурацию и вернуть полную конфигурацию"""
        async with self._uow:
            config_feature = await self._config_flag_repository.add_feature_to_config(
                config_id=config_id, **feature_data.model_dump()
            )

            # Создаем новую версию
            await self._version_repository.create_version(
                config_id=config_id,
                changelog=f"Feature {feature_data.feature_id} added to configuration",
            )

            # Возвращаем ПОЛНУЮ конфигурацию
            return await self._config_repository.get_by_id(config_id)

    async def remove_feature_from_config(self, config_id: UUID, feature_id: UUID) -> bool:
        async with self._uow:
            success = await self._config_flag_repository.remove_feature_from_config(
                config_id, feature_id
            )
            if success:
                await self._version_repository.create_version(
                    config_id=config_id,
                    changelog=f"Feature {feature_id} removed from configuration",
                )
            return success

    async def update_config_feature(
        self, config_id: UUID, feature_id: UUID, update_data: FeatureConfigFlagUpdate
    ) -> Optional[FeatureConfigFlag]:
        async with self._uow:
            update_fields = update_data.model_dump(exclude_unset=True)
            updated_feature = await self._config_flag_repository.update_config_feature(
                config_id=config_id, feature_id=feature_id, **update_fields
            )

            if updated_feature:
                await self._version_repository.create_version(
                    config_id=config_id, changelog=f"Feature {feature_id} updated in configuration"
                )

            return updated_feature

    async def get_config_features(self, config_id: UUID) -> List[FeatureConfigFlag]:
        async with self._uow:
            return await self._config_flag_repository.get_config_features(config_id)

    async def create_config_version(
        self, config_id: UUID, version_data: FeatureConfigVersionCreate
    ) -> FeatureConfigVersion:
        async with self._uow:
            return await self._version_repository.create_version(
                config_id=config_id, **version_data.model_dump()
            )

    async def get_config_versions(self, config_id: UUID) -> List[FeatureConfigVersion]:
        async with self._uow:
            return await self._version_repository.get_config_versions(config_id)
