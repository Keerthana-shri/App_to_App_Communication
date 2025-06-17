from fastapi import APIRouter, Path, Header, Depends, HTTPException
from uuid import UUID

from src.app.schemas.validation_schemas import TokenValidationRequest, TokenValidationResponse
from src.app.services.validation_service import validate_API_token
from src.app.services.consumer_services import ConsumerService

router = APIRouter(tags=["Validation"], prefix="/application")


@router.post("/{provider_id}/validate", response_model=TokenValidationResponse)
def validate_api_token_endpoint(
    provider_id: UUID = Path(..., description="Provider ID"),
    request: TokenValidationRequest = ...,
    x_api_key: str = Header(..., alias="x-api-key"),
    service: ConsumerService = Depends(ConsumerService),
):
    """
    Validate a consumer JWT token for a given provider.

    This endpoint verifies the authenticity and validity of a consumer JWT token
    using the provider's ID from the path. It is secured with the consumer's API key
    provided in the 'x-api-key' header. The API key is validated before processing the token.

    Args:

        provider_id (UUID): The unique identifier of the provider application (from the path).
        request (TokenValidationRequest): The request body containing the JWT token.
        x_api_key (str): The API key for authentication, provided in the request header.
        service (ConsumerService): The consumer service dependency for API key validation.

    Returns:

        dict: A dictionary containing the validation result and token claims (provider_id, consumer_id, permissions).

    Raises:
    
        HTTPException: If the API key is invalid, the token is invalid, expired, or the provider_id does not match.
    """
    # Validate the API key for the provider
    service._validate_consumer_secret(provider_id, x_api_key)
    result = validate_API_token(request, provider_id=provider_id)
    claims = result["claims"]
    return {
        "is_valid": result["is_valid"],
        "provider_id": claims.get("provider_id"),
        "consumer_id": claims.get("consumer_id"),
        "permissions": claims.get("permissions"),
    }
