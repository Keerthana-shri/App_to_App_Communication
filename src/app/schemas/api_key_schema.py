from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PermissionEnum(str, Enum):
    read = "read"
    write = "write"
    both = "both"


class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    revoked = "revoked"


class APIKeyCreate(BaseModel):
    provider_id: UUID
    consumer_id: UUID
    secret_hash: str
    api_key_owner_id: UUID
    permissions: PermissionEnum
    expires_at: datetime
    comment: str


class APIKeyUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    permissions: Optional[PermissionEnum] = None
    expires_at: Optional[datetime] = None
    comment: Optional[str] = None
    api_key: Optional[str] = None


class APIKeyResponse(BaseModel):
    message: str = Field(default="API key generated")
    api_key: str
    status: StatusEnum


class APIKeyDetailResponse(BaseModel):
    id: UUID
    provider_id: UUID
    consumer_id: UUID
    api_key: str
    api_key_owner_id: UUID
    permissions: PermissionEnum
    expires_at: datetime
    comment: str
    status: StatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
