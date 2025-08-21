from fastapi import APIRouter
from .feature import feature_router

router = APIRouter(prefix="/v1")

router.include_router(feature_router)
