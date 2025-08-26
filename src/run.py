if __name__ == "__main__":
    import uvicorn
    from src.config import settings

    uvicorn.run("main:app", host=settings.api.ip, port=settings.api.port, reload=True)
