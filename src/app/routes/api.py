from fastapi import APIRouter

from src.app.routes.v1 import (
    api_key_rotation_routes,
    api_key_router,
    auth_router,
    consumer_routes,
    provider_routes,
    validation_router,
)

router = APIRouter(prefix="/api/v1")


router.include_router(auth_router.router)
router.include_router(provider_routes.router)
router.include_router(consumer_routes.router)
router.include_router(api_key_router.router)
router.include_router(validation_router.router)
router.include_router(api_key_rotation_routes.router)
