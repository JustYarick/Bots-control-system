from fastapi import APIRouter, status
from dishka.integrations.fastapi import FromDishka, inject
from uuid import UUID
from typing import List

from api.v1.feature.feature_config.config_version.schema import FeatureConfigVersionCreate
from api.v1.feature.feature_config.service import FeatureConfigService
from api.v1.feature.schemas import (
    FeatureConfigVersionResponse,
)

# Feature Config routes
version_router = APIRouter(tags=["feature-config-versions"])


@version_router.get("/{config_id}/versions", response_model=List[FeatureConfigVersionResponse])
@inject
async def get_config_versions(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Получить версии конфигурации"""
    return await service.get_config_versions(config_id)


@version_router.post(
    "/{config_id}/versions",
    response_model=FeatureConfigVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_config_version(
    service: FromDishka[FeatureConfigService],
    config_id: UUID,
    version_data: FeatureConfigVersionCreate,
):
    """Создать новую версию конфигурации"""
    return await service.create_config_version(config_id, version_data)
