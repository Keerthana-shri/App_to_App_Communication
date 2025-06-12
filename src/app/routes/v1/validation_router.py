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
    Validates a consumer JWT token using provider_id from the path.
    """
    result = validate_API_token(request, provider_id=provider_id)
    claims = result["claims"]
    return {
        "is_valid": result["is_valid"],
        "provider_id": claims.get("provider_id"),
        "consumer_id": claims.get("consumer_id"),
        "permissions": claims.get("permissions"),
    }
