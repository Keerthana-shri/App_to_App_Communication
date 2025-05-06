from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class PermissionEnum(str, Enum):
    Read = "Read"
    Write = "Write"
    Both = "Both"


class APIKeyRequest(BaseModel):
    consumer_name: str
    consumer_application_id: UUID
    secret_hash: str
    provider_name: str
    provider_application_id: UUID
    permissions: PermissionEnum
    api_key_owner: str
    expires_at: datetime
    comment: str


class APIKeyResponse(BaseModel):
    message: str = Field(default="API key generated")
