from fastapi import APIRouter

from src.app.routes.v1 import consumer_routes

router = APIRouter(prefix="/api/v1")

router.include_router(consumer_routes.router)
