from fastapi import APIRouter, HTTPException, status, Query
from dishka.integrations.fastapi import FromDishka, inject
from uuid import UUID
from typing import List, Optional

from api.v1.feature_flags.schemas import (
    FeatureFlagResponse,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureConfigResponse,
    FeatureConfigCreate,
    FeatureConfigUpdate,
    FeatureConfigDetailResponse,
    FeatureConfigFlagResponse,
    FeatureConfigFlagCreate,
    FeatureConfigFlagUpdate,
    FeatureConfigVersionResponse,
    FeatureConfigVersionCreate,
    Environment,
)
from api.v1.feature_flags.service import FeatureFlagService, FeatureConfigService
from database.models import FeatureConfig
from exceptions.exceptions import FeatureFlagAlreadyExistsError, FeatureFlagNotFoundError

feature_flag_router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])
feature_config_router = APIRouter(prefix="/feature-configs", tags=["feature-configs"])


# Feature Flag routes
@feature_flag_router.get("/", response_model=List[FeatureFlagResponse])
@inject
async def get_features(
    service: FromDishka[FeatureFlagService],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Получить список функций"""
    return await service.list_features(skip=skip, limit=limit)


@feature_flag_router.post(
    "/", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_feature(service: FromDishka[FeatureFlagService], feature_data: FeatureFlagCreate):
    """Создать функцию"""
    try:
        return await service.create_feature(feature_data)
    except FeatureFlagAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@feature_flag_router.get("/{feature_id}", response_model=FeatureFlagResponse)
@inject
async def get_feature(service: FromDishka[FeatureFlagService], feature_id: UUID):
    """Получить функцию по ID"""
    feature = await service.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature flag not found")
    return feature


@feature_flag_router.get("/name/{feature_name}", response_model=FeatureFlagResponse)
@inject
async def get_feature_by_name(service: FromDishka[FeatureFlagService], feature_name: str):
    """Получить функцию по имени"""
    feature = await service.get_feature_by_name(feature_name)
    if not feature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature flag not found")
    return feature


@feature_flag_router.put("/{feature_id}", response_model=FeatureFlagResponse)
@inject
async def update_feature(
    service: FromDishka[FeatureFlagService], feature_id: UUID, update_data: FeatureFlagUpdate
):
    """Обновить функцию"""
    try:
        feature = await service.update_feature(feature_id, update_data)
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Feature flag not found"
            )
        return feature
    except FeatureFlagAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@feature_flag_router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_feature(service: FromDishka[FeatureFlagService], feature_id: UUID):
    """Удалить функцию"""
    deleted = await service.delete_feature(feature_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature flag not found")


# Feature Config routes
@feature_config_router.get("/", response_model=List[FeatureConfigResponse])
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


@feature_config_router.post(
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


@feature_config_router.get("/{config_id}", response_model=FeatureConfigDetailResponse)
@inject
async def get_config(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Получить конфигурацию со всеми функциями"""
    config = await service.get_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature config not found"
        )
    return config


@feature_config_router.put("/{config_id}", response_model=FeatureConfigResponse)
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


@feature_config_router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_config(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Удалить конфигурацию"""
    deleted = await service.delete_config(config_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature config not found"
        )


@feature_config_router.post("/{config_id}/activate", response_model=dict)
@inject
async def activate_config(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Активировать конфигурацию"""
    activated = await service.activate_config(config_id)
    if not activated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature config not found"
        )
    return {"message": "Configuration activated successfully"}


@feature_config_router.post("/{config_id}/deactivate", response_model=dict)
@inject
async def deactivate_config(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Деактивировать конфигурацию"""
    deactivated = await service.deactivate_config(config_id)
    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature config not found"
        )
    return {"message": "Configuration deactivated successfully"}


# Feature Config Features management
@feature_config_router.post(
    "/{config_id}/features",
    response_model=FeatureConfigDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def add_feature_to_config(
    service: FromDishka[FeatureConfigService],
    config_id: UUID,
    feature_data: FeatureConfigFlagCreate,
):  # Убрал -> FeatureConfigDetailResponse
    """Добавить функцию в конфигурацию"""
    try:
        # Добавляем функцию
        await service.add_feature_to_config(config_id, feature_data)

        # Возвращаем ПОЛНУЮ конфигурацию со всеми функциями
        full_config = await service.get_config(config_id)
        if not full_config:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")

        return full_config

    except FeatureFlagAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@feature_config_router.get("/{config_id}/features", response_model=List[FeatureConfigFlagResponse])
@inject
async def get_config_features(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Получить функции конфигурации"""
    return await service.get_config_features(config_id)


@feature_config_router.put(
    "/{config_id}/features/{feature_id}", response_model=FeatureConfigFlagResponse
)
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


@feature_config_router.delete(
    "/{config_id}/features/{feature_id}", status_code=status.HTTP_204_NO_CONTENT
)
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


# Versions management
@feature_config_router.get(
    "/{config_id}/versions", response_model=List[FeatureConfigVersionResponse]
)
@inject
async def get_config_versions(service: FromDishka[FeatureConfigService], config_id: UUID):
    """Получить версии конфигурации"""
    return await service.get_config_versions(config_id)


@feature_config_router.post(
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
