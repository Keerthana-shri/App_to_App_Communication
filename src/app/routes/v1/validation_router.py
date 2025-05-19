from fastapi import APIRouter, Depends

from src.app.schemas.validation_schemas import (
    ApiKeyValidationRequest,
    ConsumerValidationRequest,
    ProviderValidationRequest,
)
from src.app.services.unit_of_work import UnitOfWork
from src.app.services.validation_service import (
    validate_api_key,
    validate_consumer_app,
    validate_provider_app,
)

router = APIRouter(tags=["Validation"])


def get_unit_of_work():
    """
    Dependency function to provide a unit of work instance.

    This function is used as a dependency in route handlers to provide an instance
    of the `UnitOfWork` class, which manages database operations.

    Returns:

        UnitOfWork: An instance of the UnitOfWork class.
    """
    return UnitOfWork()


@router.post("/consumer-app")
def validate_consumer(
    request: ConsumerValidationRequest,
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
):
    """
    Endpoint to validate a consumer application.

    This endpoint validates the consumer application by checking its existence,
    verifying the secret hash, and ensuring it is of type "consumer".

    Args:

        request (ConsumerValidationRequest): The request object containing consumer_id and secret_hash.
        unit_of_work (UnitOfWork): Dependency injection for database operations.

    Returns:

        dict: A success message if validation passes.

    Raises:

        HTTPException: If validation fails due to missing or invalid data.
    """
    return validate_consumer_app(unit_of_work, request)


@router.post("/provider-app")
def validate_provider(
    request: ProviderValidationRequest,
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
):
    """
    Endpoint to validate a provider application.

    This endpoint validates the provider application by checking its existence,
    verifying the secret hash, and ensuring it is of type "provider".

    Args:

        request (ProviderValidationRequest): The request object containing provider_id and secret_hash.
        unit_of_work (UnitOfWork): Dependency injection for database operations.

    Returns:

        dict: A success message if validation passes.

    Raises:

        HTTPException: If validation fails due to missing or invalid data.
    """
    return validate_provider_app(unit_of_work, request)


@router.post("/api-key")
def validate_api_key_route(
    request: ApiKeyValidationRequest,
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
):
    """
    Endpoint to validate an API key.

    This endpoint validates the API key by checking its existence, verifying its
    active status, and ensuring it is associated with the specified provider application.

    Args:

        request (ApiKeyValidationRequest): The request object containing api_key and provider_id.
        unit_of_work (UnitOfWork): Dependency injection for database operations.

    Returns:

        dict: A dictionary containing the validation status, expiration date, and API key owner details.

    Raises:

        HTTPException: If validation fails due to missing or invalid data.
    """
    return validate_api_key(unit_of_work, request)
