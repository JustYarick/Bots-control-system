from fastapi import APIRouter
from .feature_flags.view import feature_flag_router
from .feature_flags.view import feature_config_router

router = APIRouter(prefix="/v1")

router.include_router(feature_flag_router)
router.include_router(feature_config_router)
