from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from src.app.routes import api
from src.app.services.api_key_service import APIKeyService
from src.app.services.unit_of_work import UnitOfWork

scheduler = BackgroundScheduler()
service = APIKeyService(uow=UnitOfWork())
scheduler.add_job(service.rotate_api_keys, "interval", days=7)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


app.include_router(api.router)
