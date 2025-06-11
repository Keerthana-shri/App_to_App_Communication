from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.app.routes import api
from src.app.services.api_key_service import APIKeyService
from src.app.services.unit_of_work import UnitOfWork

scheduler = BackgroundScheduler()
service = APIKeyService(uow=UnitOfWork())
scheduler.add_job(service.rotate_api_keys, "interval", days=3)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifespan of the FastAPI application.

    Starts the background scheduler when the application starts and shuts it down when the application stops.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


def custom_openapi():
    """
    Customizes the OpenAPI schema for the FastAPI application.

    Adds security schemes for JWT and x-api-key authentication and applies them to specific routes.

    Returns:
        dict: The customized OpenAPI schema.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="App-to-App Communicator",
        version="1.0.0",
        description="API documentation with JWT and x-api-key authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "x-api-key"},
    }

    for path, methods in openapi_schema["paths"].items():
        for method, details in methods.items():
            if path.startswith("/api/v1/application") and "/consumer" not in path:
                details["security"] = [{"BearerAuth": []}]
            elif path.startswith("/auth/refresh"):
                details["security"] = [{"BearerAuth": []}]
            elif "/consumer" in path:
                details["security"] = [{"ApiKeyAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(api.router)
