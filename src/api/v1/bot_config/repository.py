from typing import Optional, List, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, exists
from sqlalchemy.orm import selectinload

from api.v1.bot_config.models import BotConfig
from database.AbstractRepository import AbstractRepository
from exceptions.exceptions import BotConfigAlreadyExistsError, BotConfigNotFoundError


class BotConfigRepository(AbstractRepository[BotConfig], Protocol):
    """Интерфейс репозитория для BotConfig"""

    async def get_by_name(self, name: str) -> Optional[BotConfig]:
        """Получить конфигурацию по имени"""
        ...

    async def get_active_configs(self) -> List[BotConfig]:
        """Получить все активные конфигурации"""
        ...

    async def get_by_status(self, status: str) -> List[BotConfig]:
        """Получить конфигурации по статусу"""
        ...

    async def activate_config(self, config_id: UUID) -> bool:
        """Активировать конфигурацию"""
        ...

    async def deactivate_config(self, config_id: UUID) -> bool:
        """Деактивировать конфигурацию"""
        ...


class BotConfigRepositoryImpl(BotConfigRepository):
    """Репозиторий для работы с конфигурациями ботов"""

    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def add(self, entity: BotConfig) -> BotConfig:
        """Добавить новую сущность"""
        existing = await self.get_by_name(entity.name)
        if existing:
            raise BotConfigAlreadyExistsError(
                f"Configuration with name '{entity.name}' already exists"
            )

        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: UUID) -> Optional[BotConfig]:
        """Получить сущность по ID"""
        query = (
            select(BotConfig)
            .options(selectinload(BotConfig.versions))
            .where(BotConfig.id == entity_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BotConfig]:
        """Получить все сущности с пагинацией"""
        query = (
            select(BotConfig)
            .options(selectinload(BotConfig.versions))
            .offset(skip)
            .limit(limit)
            .order_by(BotConfig.updated_at.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(self, entity: BotConfig) -> BotConfig:
        """Обновить сущность"""
        existing = await self.get_by_id(entity.id)
        if not existing:
            raise BotConfigNotFoundError(f"Configuration with id '{entity.id}' not found")

        if existing.name != entity.name:
            name_conflict = await self.get_by_name(entity.name)
            if name_conflict and name_conflict.id != entity.id:
                raise BotConfigAlreadyExistsError(
                    f"Configuration with name '{entity.name}' already exists"
                )

        await self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Удалить сущность по ID"""
        query = delete(BotConfig).where(BotConfig.id == entity_id)
        result = await self._session.execute(query)
        return result.rowcount > 0

    async def exists(self, entity_id: UUID) -> bool:
        """Проверить существование сущности"""
        query = select(exists().where(BotConfig.id == entity_id))
        result = await self._session.execute(query)
        return result.scalar()

    async def get_by_name(self, name: str) -> Optional[BotConfig]:
        """Получить конфигурацию по имени"""
        query = (
            select(BotConfig)
            .options(selectinload(BotConfig.versions))
            .where(BotConfig.name == name)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_active_configs(self) -> List[BotConfig]:
        """Получить все активные конфигурации"""
        query = (
            select(BotConfig)
            .options(selectinload(BotConfig.versions))
            .where(BotConfig.is_active == True)
            .order_by(BotConfig.updated_at.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> List[BotConfig]:
        """Получить конфигурации по статусу"""
        query = (
            select(BotConfig)
            .options(selectinload(BotConfig.versions))
            .where(BotConfig.status == status)
            .order_by(BotConfig.updated_at.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def activate_config(self, config_id: UUID) -> bool:
        """Активировать конфигурацию"""
        query = update(BotConfig).where(BotConfig.id == config_id).values(is_active=True)
        result = await self._session.execute(query)
        return result.rowcount > 0

    async def deactivate_config(self, config_id: UUID) -> bool:
        """Деактивировать конфигурацию"""
        query = update(BotConfig).where(BotConfig.id == config_id).values(is_active=False)
        result = await self._session.execute(query)
        return result.rowcount > 0
