import logging

from fastapi import FastAPI

from app.api import health
from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.middleware import RequestIDMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    app.add_middleware(RequestIDMiddleware)
    app.include_router(health.router)
    app.include_router(v1_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
