from fastapi import APIRouter
from .view import router as feature_flags_router
from .feature_config import feature_config_router
from .feature_config.config_version.view import version_router
from .feauture_flags.view import feature_flag_router

feature_router = APIRouter()
feature_router.include_router(feature_flags_router)
feature_router.include_router(feature_config_router)
feature_router.include_router(version_router)
feature_router.include_router(feature_flag_router)
