from fastapi import APIRouter, HTTPException, status, Query
from dishka.integrations.fastapi import FromDishka, inject
from uuid import UUID
from typing import List, Optional

from api.v1.feature.feature_config.service import FeatureConfigService
from api.v1.feature.schemas import (
    FeatureConfigDetailResponse,
    FeatureConfigFlagResponse,
    FeatureConfigFlagCreate,
    FeatureConfigFlagUpdate,
)
from exceptions.exceptions import FeatureFlagAlreadyExistsError

# Feature Config routes
router = APIRouter(prefix="/feature-configs", tags=["feature-configs"])


# Feature Config Features management
@router.post(
    "/{config_id}/features",
    response_model=FeatureConfigDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def add_feature_to_config(
    service: FromDishka[FeatureConfigService],
    config_id: UUID,
    feature_data: FeatureConfigFlagCreate,
):
    """Добавить функцию в конфигурацию"""
    try:
        await service.add_feature_to_config(config_id, feature_data)

        full_config = await service.get_config(config_id)
        if not full_config:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")

        return full_config

    except FeatureFlagAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{config_id}/features", response_model=List[FeatureConfigFlagResponse])
@inject
async def get_config_features(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Получить функции конфигурации"""
    return await service.get_config_features(config_id)


@router.put("/{config_id}/features/{feature_id}", response_model=FeatureConfigFlagResponse)
@inject
async def update_config_feature(
    service: FromDishka[FeatureConfigService],
    config_id: UUID,
    feature_id: UUID,
    update_data: FeatureConfigFlagUpdate,
):
    """Обновить функцию в конфигурации"""
    feature = await service.update_config_feature(config_id, feature_id, update_data)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found in this config"
        )
    return feature


@router.delete("/{config_id}/features/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_feature_from_config(
    service: FromDishka[FeatureConfigService], config_id: UUID, feature_id: UUID
):
    """Удалить функцию из конфигурации"""
    removed = await service.remove_feature_from_config(config_id, feature_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature not found in this config"
        )
