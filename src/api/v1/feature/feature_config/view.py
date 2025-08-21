from fastapi import APIRouter, HTTPException, status, Query
from dishka.integrations.fastapi import FromDishka, inject
from uuid import UUID
from typing import List, Optional

from api.v1.feature.feature_config.schema import (
    FeatureConfigResponse,
    FeatureConfigCreate,
    FeatureConfigUpdate,
)
from api.v1.feature.feature_config.service import FeatureConfigService
from api.v1.feature.schemas import (
    FeatureConfigDetailResponse,
    Environment,
)
from exceptions.exceptions import FeatureFlagAlreadyExistsError


_feature_config_router = APIRouter(tags=["feature-configs"])


@_feature_config_router.get("/", response_model=List[FeatureConfigResponse])
@inject
async def get_configs(
    service: FromDishka[FeatureConfigService],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    environment: Optional[Environment] = Query(None),
    active_only: bool = Query(False),
):
    """Получить список конфигураций"""
    if active_only:
        return await service.get_active_configs()
    elif environment:
        return await service.get_configs_by_environment(environment)
    else:
        return await service.list_configs(skip=skip, limit=limit)


@_feature_config_router.post(
    "/", response_model=FeatureConfigResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_config(
    service: FromDishka[FeatureConfigService], config_data: FeatureConfigCreate
):
    """Создать конфигурацию"""
    try:
        return await service.create_config(config_data)
    except FeatureFlagAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@_feature_config_router.get("/{config_id}", response_model=FeatureConfigDetailResponse)
@inject
async def get_config(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Получить конфигурацию со всеми функциями"""
    config = await service.get_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature config not found"
        )
    return config


@_feature_config_router.put("/{config_id}", response_model=FeatureConfigResponse)
@inject
async def update_config(
    service: FromDishka[FeatureConfigService], config_id: UUID, update_data: FeatureConfigUpdate
):
    """Обновить конфигурацию"""
    try:
        config = await service.update_config(config_id, update_data)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Feature config not found"
            )
        return config
    except FeatureFlagAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@_feature_config_router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_config(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Удалить конфигурацию"""
    deleted = await service.delete_config(config_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature config not found"
        )


@_feature_config_router.post("/{config_id}/activate", response_model=dict)
@inject
async def activate_config(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Активировать конфигурацию"""
    activated = await service.activate_config(config_id)
    if not activated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature config not found"
        )
    return {"message": "Configuration activated successfully"}


@_feature_config_router.post("/{config_id}/deactivate", response_model=dict)
@inject
async def deactivate_config(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Деактивировать конфигурацию"""
    deactivated = await service.deactivate_config(config_id)
    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature config not found"
        )
    return {"message": "Configuration deactivated successfully"}
