from fastapi import APIRouter

from src.app.routes.v1 import consumer_routes
from src.app.routes.v1 import api_key_router

router = APIRouter(prefix="/api/v1")


router.include_router(consumer_routes.router)
router.include_router(api_key_router.router)
