from fastapi import APIRouter, status, Query
from dishka.integrations.fastapi import FromDishka, inject
from uuid import UUID
from typing import List

from api.v1.feature.feauture_flags.schema import FeatureFlagCreate, FeatureFlagUpdate
from api.v1.feature.feauture_flags.service import FeatureFlagService
from api.v1.feature.schemas import FeatureFlagResponse
from database.models import FeatureFlag

feature_flag_router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])


@feature_flag_router.get("/", response_model=List[FeatureFlagResponse])
@inject
async def get_features(
    service: FromDishka[FeatureFlagService],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[FeatureFlag]:
    """Получить список функций"""
    return await service.list_features(skip=skip, limit=limit)


@feature_flag_router.post(
    "/",
    response_model=FeatureFlagResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_feature(
    service: FromDishka[FeatureFlagService], feature_data: FeatureFlagCreate
) -> FeatureFlag:
    """Создать функцию"""
    return await service.create_feature(feature_data)


@feature_flag_router.get("/{feature_id}", response_model=FeatureFlagResponse)
@inject
async def get_feature(service: FromDishka[FeatureFlagService], feature_id: UUID) -> FeatureFlag:
    """Получить функцию по ID"""
    return await service.get_feature(feature_id)


@feature_flag_router.get("/name/{feature_name}", response_model=FeatureFlagResponse)
@inject
async def get_feature_by_name(
    service: FromDishka[FeatureFlagService], feature_name: str
) -> FeatureFlag:
    """Получить функцию по имени"""
    return await service.get_feature_by_name(feature_name)


@feature_flag_router.put("/{feature_id}", response_model=FeatureFlagResponse)
@inject
async def update_feature(
    service: FromDishka[FeatureFlagService], feature_id: UUID, update_data: FeatureFlagUpdate
) -> FeatureFlag:
    """Обновить функцию"""
    return await service.update_feature(feature_id, update_data)


@feature_flag_router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_feature(service: FromDishka[FeatureFlagService], feature_id: UUID) -> None:
    """Удалить функцию"""
    await service.delete_feature(feature_id)
