from fastapi import APIRouter

from app.api.v1 import content
from app.core.config import get_settings

router = APIRouter()
router.include_router(content.router)


@router.get("/info", tags=["meta"])
async def info() -> dict[str, str]:
    settings = get_settings()
    return {"name": settings.app_name, "version": settings.app_version}
