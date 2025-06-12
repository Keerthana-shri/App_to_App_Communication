from jose import jwt, JWTError
from fastapi import HTTPException
from uuid import UUID

from src.app.config.settings import app_config
from src.app.schemas.validation_schemas import TokenValidationRequest

def validate_API_token(
    request: "TokenValidationRequest",
    provider_id: UUID,
) -> dict:
    """
    Validates a consumer JWT token using only the provider's ID.

    Args:
        request (TokenValidationRequest): The request containing the JWT token.
        provider_id (UUID): The provider application's ID.

    Returns:
        dict: Token claims if valid.

    Raises:
        HTTPException: If the token is invalid, expired, or the provider_id does not match.
    """
    try:
        payload = jwt.decode(
            request.token,
            app_config["SECRET_KEY"],
            algorithms=[app_config["ALGORITHM"]],
        )
        if str(payload.get("provider_id")) != str(provider_id):
            raise HTTPException(status_code=401, detail="Token provider_id mismatch.")
        return {"is_valid": True, "claims": payload}
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")
