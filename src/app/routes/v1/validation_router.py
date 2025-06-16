from fastapi import APIRouter, Path
from uuid import UUID
from datetime import datetime, timezone

from src.app.schemas.validation_schemas import TokenValidationRequest, TokenValidationResponse
from src.app.services.validation_service import validate_API_token

router = APIRouter(tags=["Validation"], prefix="/application")


@router.post("/{provider_id}/validate", response_model=TokenValidationResponse)
def validate_api_token_endpoint(
    provider_id: UUID = Path(..., description="Provider ID"),
    request: TokenValidationRequest = ...,
):
    """
    Validate a consumer JWT token for a given provider.

    This endpoint verifies the authenticity and validity of a consumer JWT token
    using the provider's ID from the path. It decodes the token, checks the provider ID,
    and returns the relevant claims if the token is valid.

    Args:

        provider_id (UUID): The unique identifier of the provider application (from the path).
        request (TokenValidationRequest): The request body containing the JWT token.

    Returns:

        dict: A dictionary containing the validation result and token claims (provider_id, consumer_id, permissions).

    Raises:
    
        HTTPException: If the token is invalid, expired, or the provider_id does not match.
    """
    result = validate_API_token(request, provider_id=provider_id)
    claims = result["claims"]
    return {
        "is_valid": result["is_valid"],
        "provider_id": claims.get("provider_id"),
        "consumer_id": claims.get("consumer_id"),
        "permissions": claims.get("permissions"),
    }
