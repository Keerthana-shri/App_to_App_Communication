from fastapi import APIRouter

from src.app.routes.v1 import api_key_router

router = APIRouter(prefix="/api/v1")
