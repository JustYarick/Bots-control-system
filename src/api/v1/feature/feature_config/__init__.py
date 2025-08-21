from fastapi import APIRouter

from .view import _feature_config_router as config_router
from .config_version.view import version_router

feature_config_router = APIRouter(prefix="/feature-configs")
feature_config_router.include_router(config_router)
feature_config_router.include_router(version_router)
