from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AppType(str, Enum):
    provider = "provider"
    consumer = "consumer"


class PermissionEnum(str, Enum):
    read = "read"
    write = "write"
    both = "both"


class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    revoked = "revoked"


class APIKeyCreate(BaseModel):
    provider_id: UUID = Field(example="9384ccf4-2ca4-478c-bc38-4de5550ff052")
    secret_hash: str = Field(example="s3cr3tH@sh")
    api_key_owner_id: UUID = Field(example="072697aa-a9c8-4c5e-bb2d-c91a4f625d81")
    permissions: PermissionEnum = Field(example="read")
    expires_at: datetime = Field(example="2025-05-15")
    comment: str = Field(example="This is a sample API key.")


class APIKeyUpdate(BaseModel):
    status: Optional[StatusEnum] = Field(None, example="active")
    permissions: Optional[PermissionEnum] = Field(None, example="read")
    expires_at: Optional[datetime] = Field(None, example="2025-05-15")
    comment: Optional[str] = Field(None, example="Updated this value.")
    api_key: Optional[str] = Field(
        None,
        example="gAAAAABoJJIhIatLEuL9WRKLnWWRhDTXzzf9CI2J6-cY07qWQ9bYfUAB37C-G5NlcrJLH1ewIDKqKFqEptkUQ9brKl_X66-XKofrttbpK5hUt_mMHhKcygYz5d3dbYr1Y6F9toGKasSp",
    )


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


class APIKeyListResponse(BaseModel):
    total_pages: int
    previous_page: Optional[int]
    current_page: int
    next_page: Optional[int]
    page_size: int
    items: List[APIKeyDetailResponse]
