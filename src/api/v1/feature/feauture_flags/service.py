from typing import Protocol, List, Optional
from uuid import UUID

from api.v1.feature.feauture_flags.repository import FeatureFlagRepository
from api.v1.feature.feauture_flags.schema import FeatureFlagCreate, FeatureFlagUpdate
from database.UnitOfWork import UnitOfWork
from database.models import FeatureFlag


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
