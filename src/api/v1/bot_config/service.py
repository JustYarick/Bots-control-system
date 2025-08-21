from typing import Protocol
from typing import List, Optional
from uuid import UUID

from api.v1.bot_config.shema import BotConfigUpdate, BotConfigCreate
from database.UnitOfWork import UnitOfWork
from .models import BotConfig
from .repository import BotConfigRepository


class BotConfigService(Protocol):
    """Протокол сервиса для работы с конфигурациями ботов"""

    async def create_config(self, config_data: BotConfigCreate) -> BotConfig:
        """Создать конфигурацию"""
        ...

    async def list_configs(self, skip: int = 0, limit: int = 100) -> List[BotConfig]:
        """Получить список конфигураций с пагинацией"""
        ...

    async def get_config(self, config_id: UUID) -> Optional[BotConfig]:
        """Получить конфигурацию по ID"""
        ...

    async def get_config_by_name(self, name: str) -> Optional[BotConfig]:
        """Получить конфигурацию по имени"""
        ...

    async def update_config(
        self, config_id: UUID, update_data: BotConfigUpdate
    ) -> Optional[BotConfig]:
        """Обновить конфигурацию"""
        ...

    async def delete_config(self, config_id: UUID) -> bool:
        """Удалить конфигурацию"""
        ...

    async def get_active_configs(self) -> List[BotConfig]:
        """Получить все активные конфигурации"""
        ...

    async def get_configs_by_status(self, status: str) -> List[BotConfig]:
        """Получить конфигурации по статусу"""
        ...

    async def activate_config(self, config_id: UUID) -> bool:
        """Активировать конфигурацию"""
        ...

    async def deactivate_config(self, config_id: UUID) -> bool:
        """Деактивировать конфигурацию"""
        ...


class BotConfigServiceImpl:
    """Сервис для работы с конфигурациями ботов"""

    def __init__(self, repository: BotConfigRepository, uow: UnitOfWork):
        self._repository = repository
        self._uow = uow

    async def create_config(self, config_data: BotConfigCreate) -> BotConfig:
        """Создать конфигурацию"""
        async with self._uow:
            config = BotConfig(
                name=config_data.name,
                status=config_data.status or "draft",
                version=config_data.version or "1.0",
                is_active=config_data.is_active or False,
            )
            return await self._repository.add(config)

    async def list_configs(self, skip: int = 0, limit: int = 100) -> List[BotConfig]:
        """Получить список конфигураций с пагинацией"""
        async with self._uow:
            return await self._repository.get_all(skip=skip, limit=limit)

    async def get_config(self, config_id: UUID) -> Optional[BotConfig]:
        """Получить конфигурацию по ID"""
        async with self._uow:
            return await self._repository.get_by_id(config_id)

    async def get_config_by_name(self, name: str) -> Optional[BotConfig]:
        """Получить конфигурацию по имени"""
        async with self._uow:
            return await self._repository.get_by_name(name)

    async def update_config(
        self, config_id: UUID, update_data: BotConfigUpdate
    ) -> Optional[BotConfig]:
        """Обновить конфигурацию"""
        async with self._uow:
            # Получаем существующую конфигурацию
            config = await self._repository.get_by_id(config_id)
            if not config:
                return None

            # Обновляем только переданные поля
            update_fields = update_data.model_dump(exclude_unset=True)
            for field, value in update_fields.items():
                setattr(config, field, value)

            return await self._repository.update(config)

    async def delete_config(self, config_id: UUID) -> bool:
        """Удалить конфигурацию"""
        async with self._uow:
            return await self._repository.delete(config_id)

    async def get_active_configs(self) -> List[BotConfig]:
        """Получить все активные конфигурации"""
        async with self._uow:
            return await self._repository.get_active_configs()

    async def get_configs_by_status(self, status: str) -> List[BotConfig]:
        """Получить конфигурации по статусу"""
        async with self._uow:
            return await self._repository.get_by_status(status)

    async def activate_config(self, config_id: UUID) -> bool:
        """Активировать конфигурацию"""
        async with self._uow:
            return await self._repository.activate_config(config_id)

    async def deactivate_config(self, config_id: UUID) -> bool:
        """Деактивировать конфигурацию"""
        async with self._uow:
            return await self._repository.deactivate_config(config_id)
