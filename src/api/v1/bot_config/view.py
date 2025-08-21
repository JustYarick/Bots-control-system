from fastapi import APIRouter, HTTPException, status, Query
from dishka.integrations.fastapi import FromDishka, inject
from uuid import UUID
from typing import List, Optional

from api.v1.bot_config.shema import BotConfigResponse, BotConfigCreate, BotConfigUpdate
from api.v1.bot_config.service import BotConfigService
from exceptions.exceptions import BotConfigAlreadyExistsError, BotConfigNotFoundError

router = APIRouter(prefix="/bot_config", tags=["bot_config"])


@router.get("/", response_model=List[BotConfigResponse])
@inject
async def get_configs(
    service: FromDishka[BotConfigService],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    active_only: bool = Query(False),
):
    if active_only:
        return await service.get_active_configs()
    elif status_filter:
        return await service.get_configs_by_status(status_filter)
    else:
        return await service.list_configs(skip=skip, limit=limit)


@router.post("/", response_model=BotConfigResponse, status_code=status.HTTP_201_CREATED)
@inject
async def add_config(service: FromDishka[BotConfigService], config_data: BotConfigCreate):
    """Создать новую конфигурацию"""
    try:
        return await service.create_config(config_data)
    except BotConfigAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/name/{config_name}", response_model=BotConfigResponse)
@inject
async def get_config_by_name(service: FromDishka[BotConfigService], config_name: str):
    """Получить конфигурацию по имени"""
    config = await service.get_config_by_name(config_name)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot config not found")
    return config


@router.get("/{config_id}", response_model=BotConfigResponse)
@inject
async def get_config(service: FromDishka[BotConfigService], config_id: UUID):
    """Получить конфигурацию по ID"""
    config = await service.get_config(config_id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot config not found")
    return config


@router.put("/{config_id}", response_model=BotConfigResponse)
@inject
async def update_config(
    service: FromDishka[BotConfigService], config_id: UUID, update_data: BotConfigUpdate
):
    """Обновить конфигурацию"""
    try:
        config = await service.update_config(config_id, update_data)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Bot config not found"
            )
        return config
    except BotConfigAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BotConfigNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_config(service: FromDishka[BotConfigService], config_id: UUID):
    """Удалить конфигурацию"""
    deleted = await service.delete_config(config_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot config not found")


@router.post("/{config_id}/activate", response_model=dict)
@inject
async def activate_bot_config(service: FromDishka[BotConfigService], config_id: UUID):
    """Активировать конфигурацию"""
    activated = await service.activate_config(config_id)
    if not activated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot config not found")
    return {"message": "Configuration activated successfully"}


@router.post("/{config_id}/deactivate", response_model=dict)
@inject
async def deactivate_bot_config(service: FromDishka[BotConfigService], config_id: UUID):
    """Деактивировать конфигурацию"""
    deactivated = await service.deactivate_config(config_id)
    if not deactivated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot config not found")
    return {"message": "Configuration deactivated successfully"}
