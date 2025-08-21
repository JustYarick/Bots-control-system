from abc import abstractmethod
from typing import TypeVar, Optional, List, Protocol
from uuid import UUID

T = TypeVar("T")


class AbstractRepository(Protocol[T]):
    """Базовый абстрактный репозиторий для всех сущностей"""

    @abstractmethod
    async def add(self, entity: T) -> T:
        """Добавить новую сущность"""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Получить сущность по ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Получить все сущности с пагинацией"""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Обновить сущность"""
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Удалить сущность по ID"""
        pass

    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        """Проверить существование сущности"""
        pass
