from uuid import UUID

from fastapi import APIRouter, Depends

from src.app.services.unit_of_work import UnitOfWork
from src.app.services.validation_service import (
    validate_api_key,
    validate_consumer_app,
    validate_provider_app,
)

router = APIRouter(prefix="/validation", tags=["Validation"])


def get_unit_of_work():
    """
    Dependency function to provide a unit of work instance.

    Returns:

        UnitOfWork:
            An instance of the UnitOfWork class.
    """
    return UnitOfWork()


@router.post("/consumer")
def validate_consumer(
    consumer_id: UUID,
    secret_hash: str,
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
):
    """
    Endpoint to validate a consumer app.

    Args:

        consumer_id (UUID): The unique identifier of the consumer app.
        secret_hash (str): The hash used to validate the consumer app.
        unit_of_work (UnitOfWork): Dependency injection for unit of work.

    Returns:

        dict: A dictionary containing the validation result.

    Raises:

        HTTPException: If the validation fails or an error occurs.
    """
    return validate_consumer_app(unit_of_work, consumer_id, secret_hash)


@router.post("/provider")
def validate_provider(
    provider_id: UUID,
    secret_hash: str,
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
):
    """
    Endpoint to validate a provider app.

    Args:

        provider_id (UUID): The unique identifier of the provider app.
        secret_hash (str): The hash used to validate the provider app.
        unit_of_work (UnitOfWork): Dependency injection for unit of work.

    Returns:

        dict: A dictionary containing the validation result.

    Raises:

        HTTPException: If the validation fails or an error occurs.
    """
    return validate_provider_app(unit_of_work, provider_id, secret_hash)


@router.post("/api-key")
def validate_key(
    api_key: str,
    provider_id: UUID,
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
):
    """
    Endpoint to validate an API key.

    Args:

        api_key (str): The API key to be validated.
        provider_id (UUID): The unique identifier of the provider app.
        unit_of_work (UnitOfWork): Dependency injection for unit of work.

    Returns:

        dict: A dictionary containing the validation result.

    Raises:

        HTTPException: If the validation fails or an error occurs.
    """
    return validate_api_key(unit_of_work, api_key, provider_id)
