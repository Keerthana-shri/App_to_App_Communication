import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field


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
    provider_id: UUID4 = Field(example="40d46134-a885-4e17-91ce-0be66ce832ff")
    secret_hash: str = Field(example="8fdf8419-99e1-423e-947d-3513c1a02d92")
    api_key_owner_id: UUID4 = Field(example="37c5d3af-30e2-41d2-9dc2-b2878d4a0ca4")
    permissions: PermissionEnum = Field(example="read")
    expires_at: datetime = Field(
        example=(datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    )
    comment: str = Field(example="This is a sample API key.")


class APIKeyUpdate(BaseModel):
    status: Optional[StatusEnum] = Field(None, example="active")
    permissions: Optional[PermissionEnum] = Field(None, example="read")
    expires_at: Optional[datetime] = Field(
        None, example=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    )
    comment: Optional[str] = Field(None, example="Updated this value.")


class Response(BaseModel):
    """
    Schema for provider registration response.

    Attributes:
        message (str): Confirmation message indicating request processed successfully"
    """

    message: str = Field(example="API key updated successfully.")


class APIKeyResponse(BaseModel):
    message: str = Field(default="API key generated")
    api_key: str = Field(
        example="gAAAAABoJJIhIatLEuL9WRKLnWWRhDTXzzf9CI2J6-cY07qWQ9bYfUAB37C-G5NlcrJLH1ewIDKqKFqEptkUQ9brKl_X66-XKofrttbpK5hUt_mMHhKcygYz5d3dbYr1Y6F9toGKasSp"
    )
    status: StatusEnum


class APIKeyDetailResponse(BaseModel):
    id: UUID4 = Field(example=uuid.uuid4())
    provider_id: UUID4 = Field(example="40d46134-a885-4e17-91ce-0be66ce832ff")
    consumer_id: UUID4 = Field(example="b9fd40b8-07a3-45dc-a253-e34d7d5dd73b")
    api_key: str = Field(
        example="gAAAAABoJJIhIatLEuL9WRKLnWWRhDTXzzf9CI2J6-cY07qWQ9bYfUAB37C-G5NlcrJLH1ewIDKqKFqEptkUQ9brKl_X66-XKofrttbpK5hUt_mMHhKcygYz5d3dbYr1Y6F9toGKasSp"
    )
    api_key_owner_id: UUID4 = Field(example="37c5d3af-30e2-41d2-9dc2-b2878d4a0ca4")
    permissions: PermissionEnum
    expires_at: datetime = Field(
        example=(datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    )
    comment: str = Field(example="This is a sample API key.")
    status: StatusEnum
    created_at: datetime = Field(
        example=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    )
    updated_at: Optional[datetime] = Field(
        example=(datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    )


class APIKeyListResponse(BaseModel):
    total_pages: int = Field(example=1)
    previous_page: Optional[int] = Field(example="null")
    current_page: int = Field(example=1)
    next_page: Optional[int] = Field(example="null")
    page_size: int = Field(example=10)
    items: List[APIKeyDetailResponse]
