from uuid import UUID

from cryptography.fernet import Fernet
from fastapi import HTTPException

from src.app.config.settings import app_config
from src.app.models.data_models import StatusEnum
from src.app.services.unit_of_work import UnitOfWork
from src.app.schemas.validation_schemas import (
    ConsumerValidationRequest,
    ProviderValidationRequest,
    ApiKeyValidationRequest,
)

# Initialize the cipher suite using the encryption key
ENCRYPTION_KEY = app_config["ENCRYPTION_KEY"]
cipher_suite = Fernet(ENCRYPTION_KEY)


def validate_consumer_app(unit_of_work: UnitOfWork, request: ConsumerValidationRequest):
    """
    Validates the consumer app by checking its presence and verifying the secret hash.
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


def validate_provider_app(unit_of_work: UnitOfWork, request: ProviderValidationRequest):
    """
    Validates the provider app by checking its presence, type, and verifying the secret hash.
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


def validate_api_key(unit_of_work: UnitOfWork, request: ApiKeyValidationRequest):
    """
    Validates the API key by checking its presence, status, association with the provider app, and owner.
    """
    with unit_of_work as uow:
        key = uow.api_key.get(api_key=request.api_key)
        provider_app = uow.application.get(id=request.provider_id)

        if not key:
            raise HTTPException(status_code=404, detail="API key not found.")

        if not provider_app:
            raise HTTPException(
                status_code=404, detail="Invalid provider application."
            )
        
        if key.status != StatusEnum.active:
            raise HTTPException(status_code=403, detail="API key is not active.")

        if key.provider_id != request.provider_id:
            raise HTTPException(
                status_code=403,
                detail="API key is not associated with the specified application.",
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
