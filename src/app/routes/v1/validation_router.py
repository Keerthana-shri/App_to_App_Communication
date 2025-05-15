from uuid import UUID

from fastapi import APIRouter, Depends
from src.app.services.validation_service import (
    validate_consumer_app,
    validate_provider_app,
    validate_api_key,
)
from src.app.schemas.validation_schemas import (
    ConsumerValidationRequest,
    ProviderValidationRequest,
    ApiKeyValidationRequest,
)
from src.app.services.unit_of_work import UnitOfWork

router = APIRouter(tags=["Validation"])

def get_unit_of_work():
    """
    Dependency function to provide a unit of work instance.

    Returns:

        UnitOfWork:
            An instance of the UnitOfWork class.
    """
    return UnitOfWork()


@router.post("/consumer-app")
def validate_consumer(
    request: ConsumerValidationRequest, unit_of_work: UnitOfWork = Depends(get_unit_of_work)
):
    return validate_consumer_app(unit_of_work, request)


@router.post("/provider-app")
def validate_provider(
    request: ProviderValidationRequest, unit_of_work: UnitOfWork = Depends(get_unit_of_work)
):
    return validate_provider_app(unit_of_work, request)


@router.post("/api-key")
def validate_api_key_route(
    request: ApiKeyValidationRequest, unit_of_work: UnitOfWork = Depends(get_unit_of_work)
):
    return validate_api_key(unit_of_work, request)
