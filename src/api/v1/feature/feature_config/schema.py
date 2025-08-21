from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from api.v1.feature.schemas import Environment


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
