from fastapi import APIRouter

from src.app.routes.v1 import api_key_router, consumer_routes, provider_routes

router = APIRouter(prefix="/api/v1")


router.include_router(consumer_routes.router)
router.include_router(provider_routes.router)
router.include_router(api_key_router.router)
