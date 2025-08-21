from typing import Optional, List, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from database.models import (
    FeatureConfigVersion,
)


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
