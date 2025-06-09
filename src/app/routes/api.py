from fastapi import APIRouter

from src.app.routes.v1 import application_routes, auth_router

router = APIRouter(prefix="/api/v1")


router.include_router(auth_router.router)
router.include_router(application_routes.router)
