from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field


class AppType(str, Enum):
    """
    Enum representing the type of application.

    Attributes:
        provider (str): Represents a provider application.
        consumer (str): Represents a consumer application.
    """

    provider = "provider"
    consumer = "consumer"


class PermissionEnum(str, Enum):
    """
    Enum representing the permissions for an API key.

    Attributes:
        read (str): Read-only permission.
        write (str): Write-only permission.
        both (str): Both read and write permissions.
    """

    read = "read"
    write = "write"
    both = "both"


class StatusEnum(str, Enum):
    """
    Enum representing the status of an API key.

    Attributes:
        active (str): The API key is active.
        inactive (str): The API key is inactive.
        revoked (str): The API key has been revoked.
    """

    active = "active"
    inactive = "inactive"
    revoked = "revoked"


class APIKeyCreate(BaseModel):
    """
    Schema for creating an API key.

    Attributes:
        permissions (PermissionEnum): The permissions for the API key.
        expires_at (datetime): The expiration date of the API key.
        comment (Optional[str]): A comment or note about the API key.
        api_key_owner_id (UUID4): The ID of the user who owns the API key.
        created_by (Optional[UUID4]): The ID of the user who created the API key.
        updated_by (Optional[UUID4]): The ID of the user who last updated the API key.
    """

    permissions: PermissionEnum
    expires_at: datetime
    comment: Optional[str] = None
    api_key_owner_id: UUID4
    created_by: Optional[UUID4] = None
    updated_by: Optional[UUID4] = None


class Response(BaseModel):
    """
    Generic response schema.

    Attributes:
        message (str): A message describing the result of the operation.
    """

    message: str = Field(example="API key updated successfully.")


class APIKeyResponse(BaseModel):
    """
    Schema for the response when an API key is generated.

    Attributes:
        message (str): A message describing the result of the operation.
        api_key (str): The generated API key.
        status (StatusEnum): The status of the API key.
    """

    message: str = "API key generated"
    api_key: str
    status: StatusEnum


class APIKeyDetailResponse(BaseModel):
    """
    Schema for detailed information about an API key.

    Attributes:
        id (UUID4): The unique identifier of the API key.
        provider_id (UUID4): The ID of the provider application.
        consumer_id (UUID4): The ID of the consumer application.
        api_key_owner_id (UUID4): The ID of the user who owns the API key.
        permissions (PermissionEnum): The permissions for the API key.
        expires_at (datetime): The expiration date of the API key.
        comment (Optional[str]): A comment or note about the API key.
        status (Optional[StatusEnum]): The status of the API key.
        created_at (datetime): The timestamp when the API key was created.
        updated_at (Optional[datetime]): The timestamp when the API key was last updated.
        created_by (Optional[UUID4]): The ID of the user who created the API key.
        updated_by (Optional[UUID4]): The ID of the user who last updated the API key.
    """

    id: UUID4
    provider_id: UUID4
    consumer_id: UUID4
    api_key_owner_id: UUID4
    permissions: PermissionEnum
    expires_at: datetime
    comment: Optional[str]
    status: Optional[StatusEnum] = None
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[UUID4] = None
    updated_by: Optional[UUID4] = None


class APIKeyListResponse(BaseModel):
    """
    Schema for a paginated list of API keys.

    Attributes:
        total_pages (int): The total number of pages.
        previous_page (Optional[int]): The previous page number, if available.
        current_page (int): The current page number.
        next_page (Optional[int]): The next page number, if available.
        page_size (int): The number of items per page.
        items (List[APIKeyDetailResponse]): The list of API key details.
    """

    total_pages: int = Field(example=1)
    previous_page: Optional[int] = Field(example="null")
    current_page: int = Field(example=1)
    next_page: Optional[int] = Field(example="null")
    page_size: int = Field(example=10)
    items: List[APIKeyDetailResponse]
