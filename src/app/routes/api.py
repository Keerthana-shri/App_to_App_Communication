from fastapi import APIRouter

from src.app.routes.v1 import provider_routes

router = APIRouter(prefix="/api/v1")

router.include_router(provider_routes.router)
