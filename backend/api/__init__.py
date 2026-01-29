from fastapi import APIRouter

from .handlers import router as api_router

router = APIRouter()

router.include_router(api_router)
