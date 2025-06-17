from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query

from src.app.schemas.api_key_schema import (
    APIKeyCreate,
    APIKeyDetailResponse,
    APIKeyListResponse,
    APIKeyResponse,
)
from src.app.services.consumer_services import ConsumerService

router = APIRouter(prefix="/application", tags=["Consumer"])


@router.post("/{provider_id}/consumer/{consumer_id}", status_code=201)
def create_consumer_relationship(
    provider_id: UUID,
    consumer_id: UUID,
    data: APIKeyCreate,
    x_api_key: str = Header(..., alias="x-api-key"),
    service: ConsumerService = Depends(ConsumerService),
):
    """
    **Creates a relationship between a provider and a consumer.**

    **Args:**

        provider_id (UUID): The ID of the provider application.
        consumer_id (UUID): The ID of the consumer application.
        data (APIKeyCreate): The API key creation details.
        x_api_key (str): The API key for authentication.
        service (ConsumerService): The consumer service dependency.

    **Returns:**

        dict: A dictionary containing the details of the created relationship.

    **Raises:**

        HTTPException: If the relationship creation fails.
    """
    return service.create_relationship(
        provider_id=provider_id,
        consumer_id=consumer_id,
        data=data,
        x_api_key=x_api_key,
        current_user_id=data.api_key_owner_id,
    )


@router.get(
    "/{provider_id}/consumer/{consumer_id}/token", response_model=APIKeyResponse
)
def generate_consumer_token(
    provider_id: UUID,
    consumer_id: UUID,
    x_api_key: str = Header(..., alias="x-api-key"),
    service: ConsumerService = Depends(ConsumerService),
):
    """
    **Generates a token for a consumer application.**

    **Args:**

        provider_id (UUID): The ID of the provider application.
        consumer_id (UUID): The ID of the consumer application.
        x_api_key (str): The API key for authentication.
        service (ConsumerService): The consumer service dependency.

    **Returns:**

        APIKeyResponse: The generated token details.

    **Raises:**

        HTTPException: If token generation fails.
    """
    return service.generate_token(
        provider_id=provider_id,
        consumer_id=consumer_id,
        x_api_key=x_api_key,
    )


@router.get(
    "/{provider_id}/consumer/{consumer_id}", response_model=APIKeyDetailResponse
)
def get_consumer_by_id(
    provider_id: UUID,
    consumer_id: UUID,
    x_api_key: str = Header(..., alias="x-api-key"),
    service: ConsumerService = Depends(ConsumerService),
):
    """
    **Retrieves details of a consumer application by its ID.**

    **Args:**

        provider_id (UUID): The ID of the provider application.
        consumer_id (UUID): The ID of the consumer application.
        x_api_key (str): The API key for authentication.
        service (ConsumerService): The consumer service dependency.

    **Returns:**

        APIKeyDetailResponse: The consumer application details.

    **Raises:**

        HTTPException: If the consumer application is not found.
    """
    return service.get_consumer(
        provider_id=provider_id,
        consumer_id=consumer_id,
        x_api_key=x_api_key,
    )


@router.get("/{provider_id}/consumer/", response_model=APIKeyListResponse)
def get_all_consumers_for_provider(
    provider_id: UUID,
    x_api_key: str = Header(..., alias="x-api-key"),
    page: int = 1,
    page_size: int = 10,
    sort_by: str = Query(
        "created_at", enum=["name", "status", "created_at", "updated_at"]
    ),
    order: str = Query("asc", enum=["asc", "desc"]),
    service: ConsumerService = Depends(ConsumerService),
):
    """
    **Retrieves all consumers for a provider application with pagination.**

    **Args:**

        provider_id (UUID): The ID of the provider application.
        x_api_key (str): The API key for authentication.
        page (int): The page number for pagination. Defaults to 1.
        page_size (int): The number of items per page. Defaults to 10.
        sort_by (str): The field to sort by. Defaults to "created_at".
        order (str): The sort order ("asc" or "desc"). Defaults to "asc".
        service (ConsumerService): The consumer service dependency.

    **Returns:**

        APIKeyListResponse: A response object containing the list of consumers and pagination details.

    **Raises:**

        HTTPException: If the retrieval fails.
    """
    return service.get_all_consumers(
        provider_id=provider_id,
        x_api_key=x_api_key,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
    )
