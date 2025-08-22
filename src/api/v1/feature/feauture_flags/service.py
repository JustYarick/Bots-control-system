from typing import Protocol, List, Optional
from uuid import UUID

from api.v1.feature.feauture_flags.repository import FeatureFlagRepository
from api.v1.feature.feauture_flags.schema import FeatureFlagCreate, FeatureFlagUpdate
from database.UnitOfWork import UnitOfWork
from database.models import FeatureFlag
from exceptions.exceptions import FeatureFlagNotFoundError, FeatureFlagAlreadyExistsError


class FeatureFlagService(Protocol):
    """Протокол сервиса для работы с функциями"""

    async def create_feature(self, feature_data: FeatureFlagCreate) -> FeatureFlag:
        """Создать функцию. Поднимает FeatureFlagAlreadyExistsError если уже существует"""
        ...

    async def list_features(self, skip: int = 0, limit: int = 100) -> List[FeatureFlag]:
        """Получить список функций"""
        ...

    async def get_feature(self, feature_id: UUID) -> FeatureFlag:
        """Получить функцию по ID. Поднимает FeatureFlagNotFoundError если не найдена"""
        ...

    async def get_feature_by_name(self, name: str) -> FeatureFlag:
        """Получить функцию по имени. Поднимает FeatureFlagNotFoundError если не найдена"""
        ...

    async def update_feature(self, feature_id: UUID, update_data: FeatureFlagUpdate) -> FeatureFlag:
        """Обновить функцию. Поднимает FeatureFlagNotFoundError или FeatureFlagAlreadyExistsError"""
        ...

    async def delete_feature(self, feature_id: UUID) -> None:
        """Удалить функцию. Поднимает FeatureFlagNotFoundError если не найдена"""
        ...


class FeatureFlagServiceImpl(FeatureFlagService):
    """Сервис для работы с функциями"""

    def __init__(self, repository: FeatureFlagRepository, uow: UnitOfWork):
        self._repository = repository
        self._uow = uow

    async def create_feature(self, feature_data: FeatureFlagCreate) -> FeatureFlag:
        async with self._uow:
            # Проверяем на дубликат по имени
            existing_feature = await self._repository.get_by_name(feature_data.name)
            if existing_feature:
                raise FeatureFlagAlreadyExistsError(feature_data.name)

            feature = FeatureFlag(**feature_data.model_dump())
            return await self._repository.add(feature)

    async def list_features(self, skip: int = 0, limit: int = 100) -> List[FeatureFlag]:
        async with self._uow:
            return await self._repository.get_all(skip=skip, limit=limit)

    async def get_feature(self, feature_id: UUID) -> FeatureFlag:
        async with self._uow:
            feature = await self._repository.get_by_id(feature_id)
            if not feature:
                raise FeatureFlagNotFoundError(str(feature_id))
            return feature

    async def get_feature_by_name(self, name: str) -> FeatureFlag:
        async with self._uow:
            feature = await self._repository.get_by_name(name)
            if not feature:
                raise FeatureFlagNotFoundError(name)
            return feature

    async def update_feature(self, feature_id: UUID, update_data: FeatureFlagUpdate) -> FeatureFlag:
        async with self._uow:
            # Проверяем существование feature
            feature = await self._repository.get_by_id(feature_id)
            if not feature:
                raise FeatureFlagNotFoundError(str(feature_id))

            update_fields = update_data.model_dump(exclude_unset=True)

            # Если обновляем имя, проверяем на дубликат
            if "name" in update_fields and update_fields["name"] != feature.name:
                existing_with_name = await self._repository.get_by_name(update_fields["name"])
                if existing_with_name:
                    raise FeatureFlagAlreadyExistsError(update_fields["name"])

            # Применяем изменения
            for field, value in update_fields.items():
                setattr(feature, field, value)

            return await self._repository.update(feature)

    async def delete_feature(self, feature_id: UUID) -> None:
        async with self._uow:
            # Проверяем существование перед удалением
            feature = await self._repository.get_by_id(feature_id)
            if not feature:
                raise FeatureFlagNotFoundError(str(feature_id))

            # Удаляем
            deleted = await self._repository.delete(feature_id)
            if not deleted:  # На случай если repository.delete вернет False
                raise FeatureFlagNotFoundError(str(feature_id))
