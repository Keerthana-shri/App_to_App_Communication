from fastapi import HTTPException
from uuid import UUID
from passlib.hash import bcrypt
from src.app.services.unit_of_work import UnitOfWork


def validate_consumer_app(unit_of_work: UnitOfWork, consumer_id: UUID, secret_hash: str):
    """
    Validates the consumer app by checking its presence and verifying the secret hash.
    Args:
        unit_of_work (UnitOfWork): Database session and repository manager.
        consumer_id (UUID): Unique identifier of the consumer app.
        secret_hash (str): Secret hash of the consumer app.
    Raises:
        HTTPException: If the consumer app is not valid.
    """
    with unit_of_work as uow:
        consumer_app = uow.application.get(id=consumer_id)

        if not consumer_app:
            raise HTTPException(status_code=404, detail="Consumer application not found.")
        print(consumer_app.secret_hash, secret_hash)
        if not bcrypt.verify(secret_hash, consumer_app.secret_hash):
            raise HTTPException(status_code=403, detail="Invalid secret hash for consumer application.")

        if consumer_app.type.value != "consumer":
            raise HTTPException(status_code=403, detail="Application is not a consumer app.")

    return {"message": "Consumer application validated successfully."}


def validate_provider_app(unit_of_work: UnitOfWork, provider_id: UUID, secret_hash: str):
    """
    Validates the provider app by checking its presence, type, and verifying the secret hash.
    Args:
        unit_of_work (UnitOfWork): Database session and repository manager.
        provider_id (UUID): Unique identifier of the provider app.
        secret_hash (str): Secret hash of the provider app.
    Raises:
        HTTPException: If the provider app is not valid.
    """
    with unit_of_work as uow:
        provider_app = uow.application.get(id=provider_id)

        if not provider_app:
            raise HTTPException(status_code=404, detail="Provider application not found.")
        
        if not bcrypt.verify(secret_hash, provider_app.secret_hash):
            raise HTTPException(status_code=403, detail="Invalid secret hash for provider application.")

        if provider_app.type.value != "provider":
            raise HTTPException(status_code=403, detail="Application is not a provider app.")

    return {"message": "Provider application validated successfully."}


def validate_api_key(unit_of_work: UnitOfWork, api_key: str):
    """
    Validates the API key by checking its presence, status, and association with the provider app.
    Args:
        unit_of_work (UnitOfWork): Database session and repository manager.
        api_key (str): The API key to validate.
        provider_id (UUID): Unique identifier of the provider app.
    Raises:
        HTTPException: If the API key is not valid.
    """
    with unit_of_work as uow:
        key = uow.api_key.get_by_key(api_key)

        if not key:
            raise HTTPException(status_code=404, detail="API key not found.")

        if key.status.value != "active":
            raise HTTPException(status_code=403, detail="API key is not active.")

    return {"message": "API key validated successfully."}