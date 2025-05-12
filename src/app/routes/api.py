from fastapi import APIRouter

from src.app.routes.v1.validation_router import router as validation_router

router = APIRouter()
router.include_router(validation_router)  

