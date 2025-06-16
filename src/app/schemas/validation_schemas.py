from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class TokenValidationRequest(BaseModel):
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

class TokenValidationResponse(BaseModel):
    """
    Schema for custom token claims.

    Attributes:
        is_valid (bool): Indicates whether the token is valid.
        provider_id (UUID): The ID of the provider.
        consumer_id (UUID): The ID of the consumer.
        permissions (str): The permissions assigned to the token.
    """
    is_valid: bool
    provider_id: UUID
    consumer_id: UUID
    permissions: str
    

