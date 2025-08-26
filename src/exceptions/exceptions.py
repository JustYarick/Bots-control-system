from datetime import datetime

from pydantic import BaseModel


class BaseAPIException(Exception):
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FeatureFlagAlreadyExistsError(BaseAPIException):
    def __init__(self, feature_name: str):
        super().__init__(
            message=f"Feature flag with name '{feature_name}' already exists",
            error_code="FEATURE_FLAG_ALREADY_EXISTS",
        )


class FeatureFlagNotFoundError(BaseAPIException):
    def __init__(self, identifier: str):
        super().__init__(
            message=f"Feature flag '{identifier}' not found", error_code="FEATURE_FLAG_NOT_FOUND"
        )


class ApiError(BaseModel):
    error_code: str
    message: str
    path: str
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
