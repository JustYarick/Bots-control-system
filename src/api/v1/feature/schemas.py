from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

from api.v1.feature.feature_config.config_version.schema import FeatureConfigVersionResponse
from api.v1.feature.feauture_flags.schema import FeatureFlagResponse


class Environment(str, Enum):
    """Доступные окружения"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class FeatureConfigFlagCreate(BaseModel):
    feature_id: UUID
    is_enabled: bool = Field(default=False)
    is_free: bool = Field(default=False)
    disabled_message: Optional[str] = Field(None, max_length=256)


class FeatureConfigFlagUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    is_free: Optional[bool] = None
    disabled_message: Optional[str] = Field(None, max_length=256)


class FeatureConfigFlagResponse(BaseModel):
    config_id: UUID
    feature_id: UUID
    is_enabled: bool
    is_free: bool
    disabled_message: Optional[str]
    created_at: datetime

    feature: FeatureFlagResponse

    class Config:
        from_attributes = True


# ========================
# Complex response schemas
# ========================


class FeatureConfigDetailResponse(BaseModel):
    """Полная информация о конфигурации с функциями и версиями"""

    id: UUID
    name: str
    environment: Environment
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    features: List[FeatureConfigFlagResponse]
    versions: List[FeatureConfigVersionResponse]

    class Config:
        from_attributes = True


# ========================
# Bulk operations schemas
# ========================


class BulkFeatureToggle(BaseModel):
    """Схема для массового включения/отключения функций"""

    feature_ids: List[UUID]
    is_enabled: bool


class BulkFeatureUpdate(BaseModel):
    """Схема для массового обновления настроек функций"""

    updates: List[dict]  # [{"feature_id": UUID, "is_enabled": bool, "is_free": bool}]


# ========================
# Filter schemas
# ========================


class FeatureConfigFilter(BaseModel):
    """Фильтры для поиска конфигураций"""

    environment: Optional[Environment] = None
    is_active: Optional[bool] = None
    name_contains: Optional[str] = None


class FeatureFlagFilter(BaseModel):
    """Фильтры для поиска функций"""

    name_contains: Optional[str] = None
    in_config: Optional[UUID] = None  # UUID конфигурации
