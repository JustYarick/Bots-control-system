from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


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
