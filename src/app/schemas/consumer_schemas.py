import enum
import uuid
from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field


class ConsumerRegisterRequest(BaseModel):
    """
    Schema for consumer registration request.

    Attributes:
        application_name (str): Name of the application being registered.
        application_guid (UUID4): Unique identifier for the provided application.
        application_secret (UUID4): Secret key for authentication, auto-generated if not provided.
        comments (str): Additional information regarding the application.
    """

    application_name: str = Field(..., min_length=3, example="Audience Explorer")
    application_guid: UUID4 = Field(
        default_factory=uuid.uuid4, example="b9fd40b8-07a3-45dc-a253-e34d7d5dd73b"
    )
    application_secret: UUID4 = Field(
        default_factory=uuid.uuid4, example=str(uuid.uuid4())
    )
    user_id: UUID4 = Field(
        default_factory=uuid.uuid4, example="96e5fed6-9507-486b-8903-7d449bceac46"
    )
    comments: str = Field(
        ...,
        example="An Audience Explorer application helps users analyze and segment their target audience efficiently, using data-driven insights to improve engagement strategies.",
    )


class Response(BaseModel):
    """
    Schema for provider registration response.

    Attributes:
        message (str): Confirmation message indicating request processed successfully"
    """

    message: str = Field(example="Request processed successfully")


class SortByEnum(enum.Enum):
    """
    Defines sortable fields for consumer queries.

    Attributes:
        name (str): Sort by consumer name.
        status (str): Sort by consumer status.
        created_at (str): Sort by creation timestamp.
        updated_at (str): Sort by updated timestamp.
    """

    name = "name"
    status = "status"
    created_at = "created_at"
    updated_at = "updated_at"


class OrderEnum(enum.Enum):
    """
    Defines the sorting order for consumer queries.

    Attributes:
        asc (str): Sort results in ascending order.
        desc (str): Sort results in descending order.
    """

    asc = "asc"
    desc = "desc"


class StatusEnum(enum.Enum):
    """
    Enum representing the status of an entity.
    - active: Entity is active.
    - inactive: Entity is inactive.
    - revoked: Entity access has been revoked.
    """

    active = "active"
    inactive = "inactive"
    revoked = "revoked"


class ConsumerDetailsResponse(BaseModel):
    """
    Represents the response model for consumer details.

    Attributes:
        id (UUID4): Unique identifier of the consumer.
        name (str): Name of the consumer.
        status (StatusEnum): Current status of the consumer (active, inactive, revoked).
        user_id (UUID4): Unique identifier of the associated user.
        comment (str): Additional comments or notes related to the consumer.
        created_at (datetime): Timestamp when the consumer was created.
        updated_at (datetime): Timestamp when the consumer was last updated.
    """

    id: UUID4 = Field(
        default_factory=uuid.uuid4, example="40d46134-a885-4e17-91ce-0be66ce832ff"
    )
    name: str = Field(..., example="Report Builder")
    status: StatusEnum = Field(..., example="active")
    user_id: UUID4 = Field(
        default_factory=uuid.uuid4, example="96e5fed6-9507-486b-8903-7d449bceac46"
    )
    comment: str = Field(
        ...,
        example="A Report Builder streamlines data visualization and reporting, allowing users to generate structured, customizable reports efficiently. It enhances decision-making by providing clear insights through dynamic filtering, aggregation, and export options.",
    )
    created_at: datetime = Field(..., example="2025-05-09 18:38:02.001 +0530")
    updated_at: Optional[datetime] = Field(
        default=None, example="2025-05-09 20:38:10.059 +0530"
    )

    class Config:
        """
        Configuration settings for Pydantic model serialization.

        Attributes:
            from_attributes (bool): Enables model population from ORM objects.
            json_encoders (dict): Defines custom JSON serialization rules for datetime fields.
                - Converts datetime objects into a formatted string: "YYYY-MM-DD HH:MM:SS.sss +TZ".
        """

        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S.%f %z")}


class ConsumerUpdateRequest(BaseModel):
    """
    Represents the request model for updating consumer details.

    Attributes:
        name (Optional[str]): The updated name of the consumer.
        status (Optional[str]): The updated status of the consumer. Expected values: "active", "inactive", "revoked"
        comment (Optional[str]): comments or notes regarding the consumer to update.
        user_id (Optional[UUID4]): unique identifier of the associated user with application.

    """

    name: Optional[str] = Field(None, example="Reports and Insights")
    status: Optional[str] = Field(None, example="active")
    comment: Optional[str] = Field(None, example="New comment for the consumer.")
    user_id: Optional[UUID4] = Field(
        None, example="817d5459-a5e3-46af-b5fb-22899c530e09"
    )


class PaginatedResponse(BaseModel):
    """
    Represents a paginated response model for API results.

    Attributes:
        total_pages (int): Total number of pages available based on the dataset.
        previous_page (Optional[int]): The page number before the current one, if applicable.
        current_page (int): The current page number being accessed.
        next_page (Optional[int]): The page number after the current one, if available.
        page_size (int): Number of items per page.
        items (list[ConsumerDetailsResponse]): The list of items retrieved for the current page.
    """

    total_pages: int
    previous_page: Optional[int]
    current_page: int
    next_page: Optional[int]
    page_size: int
    items: list[ConsumerDetailsResponse]


class ApiKeyResponse(BaseModel):
    """
    Represents the response model for API key details.

    Attributes:
        x_api_key (str): The generated API key of provider for the consumer.
    """

    x_api_key: str


class ApiKeyRequest(BaseModel):
    """
    Represents the request model for API key details.

    Attributes:
        application_secret (UUID4): The consumer secret key for authentication.
        provider_id (UUID4): The unique identifier of the provider application.
    """

    application_secret: UUID4 = Field(
        default_factory=uuid.uuid4, example=str(uuid.uuid4())
    )
    provider_id: UUID4 = Field(
        default_factory=uuid.uuid4, example="40d46134-a885-4e17-91ce-0be66ce832ff"
    )
