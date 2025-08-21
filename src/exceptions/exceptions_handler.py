from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409, content={"detail": "Duplicate entry or constraint violation"}
    )


def setup_exception_handlers(app: FastAPI):
    """Регистрирует все обработчики исключений"""
    app.add_exception_handler(IntegrityError, integrity_error_handler)
