from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.schemas.validation_schemas import (
    ApiKeyValidationRequest,
    ProviderValidationRequest,
)
from src.app.services.unit_of_work import UnitOfWork
from src.app.services.validation_service import (
    validate_api_key_service,
    validate_provider_app,
)

router = APIRouter(tags=["Validation"], prefix="/validations")


def get_unit_of_work():
    """
    Dependency function to provide a unit of work instance.

    This function is used as a dependency in route handlers to provide an instance
    of the `UnitOfWork` class, which manages database operations.

    Returns:

        UnitOfWork: An instance of the UnitOfWork class.
    """
    return UnitOfWork()


@router.post("/provider")
def validate_provider(
    request: ProviderValidationRequest,
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """
    **Endpoint to validate a provider application.**

    This endpoint validates the provider application by checking its existence,
    verifying the secret hash, and ensuring it is of type "provider".

    **Args**:

        request (ProviderValidationRequest): The request object containing provider_id and secret_hash.
        unit_of_work (UnitOfWork): Dependency injection for database operations.

    **Returns**:

        dict: A success message if validation passes.

    **Raises**:

        HTTPException: If validation fails due to missing or invalid data.
    """
    return validate_provider_app(unit_of_work, request)


@router.post("/api-key")
def validate_api_key(
    request: ApiKeyValidationRequest,
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """
    **Endpoint to validate an API key.**

    This endpoint validates the API key by checking its existence, verifying its
    active status, and ensuring it is associated with the specified provider application.

    **Args**:

        request (ApiKeyValidationRequest): The request object containing api_key and provider_id.
        unit_of_work (UnitOfWork): Dependency injection for database operations.

    **Returns**:

        dict: A dictionary containing the validation status, expiration date, and API key owner details.

    **Raises**:

        HTTPException: If validation fails due to missing or invalid data.
    """
    return validate_api_key_service(unit_of_work, request)
