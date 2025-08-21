from fastapi import APIRouter, HTTPException, status, Query
from dishka.integrations.fastapi import FromDishka, inject
from uuid import UUID
from typing import List

from api.v1.feature.feauture_flags.schema import FeatureFlagCreate, FeatureFlagUpdate
from api.v1.feature.feauture_flags.service import FeatureFlagService
from api.v1.feature.schemas import (
    FeatureFlagResponse,
)
from exceptions.exceptions import FeatureFlagAlreadyExistsError


feature_flag_router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])


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
