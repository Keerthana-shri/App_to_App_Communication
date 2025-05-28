from cryptography.fernet import Fernet
from fastapi import HTTPException

from src.app.config.settings import app_config
from src.app.models.data_models import StatusEnum
from src.app.schemas.validation_schemas import (
    ApiKeyValidationRequest,
    ConsumerValidationRequest,
    ProviderValidationRequest,
)
from src.app.services.logging_service import log_activity
from src.app.services.unit_of_work import UnitOfWork

# Initialize the cipher suite using the encryption key
ENCRYPTION_KEY = app_config["ENCRYPTION_KEY"]
cipher_suite = Fernet(ENCRYPTION_KEY)


def validate_consumer_app(unit_of_work: UnitOfWork, request: ConsumerValidationRequest):
    """
    Validates the consumer application.

    This function checks the following:
    1. Whether the consumer application exists in the database.
    2. Whether the provided secret hash matches the decrypted secret hash stored in the database.
    3. Whether the application type is "consumer".

    Args:

        unit_of_work (UnitOfWork): The unit of work instance for database operations.
        request (ConsumerValidationRequest): The request object containing consumer_id and secret_hash.

    Returns:

        dict: A success message if validation passes.

    Raises:

        HTTPException: If the consumer application is not found, the secret hash is invalid,
                       or the application type is not "consumer".
    """
    with unit_of_work as uow:
        consumer_app = uow.application.get(id=request.consumer_id)

        if not consumer_app:
            raise HTTPException(
                status_code=404, detail="Consumer application not found."
            )

        try:
            decrypted_secret = cipher_suite.decrypt(consumer_app.secret_hash).decode()
            if decrypted_secret != request.secret_hash:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid secret hash for consumer application.",
                )
        except Exception:
            raise HTTPException(
                status_code=403, detail="Invalid secret hash for consumer application."
            )

        if consumer_app.type.value != "consumer":
            raise HTTPException(
                status_code=403, detail="Application is not a consumer app."
            )

    return {"message": "Consumer application validated successfully."}


def validate_provider_app(
    unit_of_work: UnitOfWork, request: ProviderValidationRequest
) -> dict:
    """
    Validates the provider application.

    This function checks the following:
    1. Whether the provider application exists in the database.
    2. Whether the provided secret hash matches the decrypted secret hash stored in the database.
    3. Whether the application type is "provider".

    Args:
        unit_of_work (UnitOfWork): The unit of work instance for database operations.
        request (ProviderValidationRequest): The request object containing provider_id and secret_hash.

    Returns:
        dict: A success message if validation passes.

    Raises:
        HTTPException: If the provider application is not found, the secret hash is invalid,
                       or the application type is not "provider".
    """
    with unit_of_work as uow:
        provider_app = uow.application.get(id=request.provider_id)

        if not provider_app:
            raise HTTPException(
                status_code=404, detail="Provider application not found."
            )

        try:
            decrypted_secret = cipher_suite.decrypt(provider_app.secret_hash).decode()
            print(f"Decrypted secret: {decrypted_secret}")
            if decrypted_secret != request.secret_hash:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid secret hash for provider application.",
                )
        except Exception:
            raise HTTPException(
                status_code=403, detail="Invalid secret hash for provider application."
            )

        if provider_app.type.value != "provider":
            raise HTTPException(
                status_code=403, detail="Application is not a provider app."
            )

    return {"message": "Provider application validated successfully."}


def validate_api_key_service(
    unit_of_work: UnitOfWork, request: ApiKeyValidationRequest
) -> dict:
    """
    Validates the API key.

    This function checks the following:
    1. Whether the API key exists in the database.
    2. Whether the API key is active.
    3. Whether the API key is associated with the specified provider application.
    4. Retrieves the owner details of the API key.

    Args:
        unit_of_work (UnitOfWork): The unit of work instance for database operations.
        request (ApiKeyValidationRequest): The request object containing api_key and provider_id.

    Returns:
        dict: A dictionary containing the validation status, expiration date, and API key owner details.

    Raises:
        HTTPException: If the API key is not found, is inactive, or is not associated with the specified provider application.
    """
    validate_provider_app(request=request, unit_of_work=unit_of_work)
    with unit_of_work as uow:
        print(request)
        key = uow.api_key.get(api_key=request.api_key)
        provider_app = uow.application.get(id=request.provider_id)

        if not key:
            raise HTTPException(status_code=404, detail="API key not found.")

        if not provider_app:
            raise HTTPException(status_code=404, detail="Invalid provider application.")

        if key.status != StatusEnum.active:
            raise HTTPException(status_code=403, detail="API key is not active.")

        if key.provider_id != request.provider_id:
            raise HTTPException(
                status_code=403,
                detail="API key is not associated with the specified application.",
            )

        api_key = uow.api_key.get(api_key=request.api_key)
        log_activity(
            unit_of_work=uow,
            application_id=api_key.consumer_id,
            description=f"API key '{request.api_key}' validated for consumer '{api_key.consumer_id}' and provider '{api_key.provider_id}'.",
        )

        return {
            "is_valid": True,
            "expires_at": key.expires_at,
            "api_key_owner": {
                "id": key.api_key_owner_id,
                "name": key.owner.name,
                "email": key.owner.email,
            },
        }
