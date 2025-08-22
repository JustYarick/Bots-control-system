from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime

from exceptions.exceptions import (
    FeatureFlagAlreadyExistsError,
    FeatureFlagNotFoundError,
    BaseAPIException,
    ApiError,
)


def create_error_response(
    request: Request, exc: BaseAPIException, status_code: int
) -> JSONResponse:
    """Создает стандартный ответ об ошибке"""
    error = ApiError(
        error_code=exc.error_code or "UNKNOWN_ERROR",
        message=exc.message,
        path=request.url.path,
        timestamp=datetime.now(),
    )

    return JSONResponse(status_code=status_code, content=jsonable_encoder(error.dict()))


async def feature_flag_not_found_handler(request: Request, exc: FeatureFlagNotFoundError):
    return create_error_response(request, exc, status.HTTP_404_NOT_FOUND)


async def feature_flag_already_exists_handler(request: Request, exc: FeatureFlagAlreadyExistsError):
    return create_error_response(request, exc, status.HTTP_409_CONFLICT)


def setup_exception_handlers(app: FastAPI):
    """Регистрирует все обработчики исключений"""
    app.add_exception_handler(FeatureFlagNotFoundError, feature_flag_not_found_handler)
    app.add_exception_handler(FeatureFlagAlreadyExistsError, feature_flag_already_exists_handler)
