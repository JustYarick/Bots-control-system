from fastapi import APIRouter
from .bot_config.view import router as bot_config_router

router = APIRouter(prefix="/v1")

router.include_router(bot_config_router)
