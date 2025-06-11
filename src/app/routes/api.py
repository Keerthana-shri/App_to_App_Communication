from fastapi import APIRouter

from src.app.routes.v1 import application_routes, auth_router, consumer_routes

router = APIRouter(prefix="/api/v1")


router.include_router(auth_router.router)
router.include_router(application_routes.router)
router.include_router(consumer_routes.router)
