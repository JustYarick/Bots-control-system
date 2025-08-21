from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class BotConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, description="Уникальное имя конфигурации")
    status: Optional[str] = Field("draft", max_length=32, description="Статус конфигурации")
    version: Optional[str] = Field("1.0", max_length=32, description="Версия конфигурации")
    is_active: Optional[bool] = Field(False, description="Активна ли конфигурация")


class BotConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    status: Optional[str] = Field(None, max_length=32)
    version: Optional[str] = Field(None, max_length=32)
    is_active: Optional[bool] = None


class BotConfigResponse(BaseModel):
    id: UUID
    name: str
    status: str
    version: str
    is_active: bool
    updated_at: datetime

    class Config:
        from_attributes = True
