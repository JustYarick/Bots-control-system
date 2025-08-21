from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class Environment(str, Enum):
    """Доступные окружения"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


# =====================
# Feature Flag schemas
# =====================


class FeatureFlagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: Optional[str] = Field(None, max_length=256)


class FeatureFlagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = Field(None, max_length=256)


class FeatureFlagResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================
# Feature Config schemas
# =====================


class FeatureConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    environment: Environment
    description: Optional[str] = Field(None, max_length=256)
    is_active: bool = Field(False)


class FeatureConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = Field(None, max_length=256)
    is_active: Optional[bool] = None


class FeatureConfigResponse(BaseModel):
    id: UUID
    name: str
    environment: Environment
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================
# Feature Config Flag schemas
# =============================


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


# ================================
# Feature Config Version schemas
# ================================


class FeatureConfigVersionCreate(BaseModel):
    changelog: Optional[str] = None
    created_by: Optional[str] = Field(None, max_length=64)


class FeatureConfigVersionResponse(BaseModel):
    id: int
    config_id: UUID
    version_number: int
    changelog: Optional[str]
    created_by: Optional[str]
    created_at: datetime

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
