from fastapi import APIRouter

from src.app.schemas.api_key_schema import APIKeyRequest
from src.app.services.api_key_service import APIKeyService
from src.app.services.unit_of_work import APIKeyUnitOfWork

router = APIRouter(tags=["API Key Management Routes"])


@router.post("/consumer/api-key")
def generate_api_key(request: APIKeyRequest):
    """
    API route to generate a new API key.

    Parameters:
        request (APIKeyRequest): The API key details from the request body.

    Returns:
        dict: Success message.
    """
    with APIKeyUnitOfWork() as unit_of_work:
        service = APIKeyService(uow=unit_of_work)
        message = service.generate_api_key(
            consumer_name=request.consumer_name,
            consumer_application_id=request.consumer_application_id,
            secret_hash=request.secret_hash,
            provider_name=request.provider_name,
            provider_application_id=request.provider_application_id,
            permissions=request.permissions,
            api_key_owner=request.api_key_owner,
            expires_at=request.expires_at,
            comment=request.comment,
        )
        return {"message": message}
