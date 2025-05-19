from uuid import UUID

from fastapi import APIRouter, Query

import src.app.services.consumer_services as consumer_services
from src.app.schemas.consumer_schemas import (
    ApiKeyRequest,
    ApiKeyResponse,
    ConsumerDetailsResponse,
    ConsumerRegisterRequest,
    ConsumerUpdateRequest,
    OrderEnum,
    PaginatedResponse,
    Response,
    SortByEnum,
)
from src.app.services.unit_of_work import UnitOfWork

router = APIRouter(tags=["Consumer"])


@router.post("/consumers", response_model=Response, status_code=201)
def register_consumer(data: ConsumerRegisterRequest):
    """Registers a consumer application.

    This endpoint handles the registration of a consumer application. It validates the provided application details, ensures no duplicate registration, and securely stores relevant information.

    Args:

        data (ConsumerRegisterRequest):
            The request payload containing application details.

    Returns:

        ConsumerRegisterResponse:
            The response confirming successful registration.

    Raises:

        HTTPException:
            If validation fails or the application is already registered.
    """

    unit_of_work = UnitOfWork()
    return consumer_services.register_consumer(
        unit_of_work=unit_of_work,
        data=data,
    )


@router.get("/consumers", response_model=PaginatedResponse)
def get_all_consumers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=5, le=100),
    sort_by: SortByEnum = Query(SortByEnum.created_at),
    order: OrderEnum = Query(OrderEnum.asc),
):
    """
    Retrieve a paginated list of consumers.

    This endpoint returns a list of consumers with optional pagination, sorting, and ordering.

    Parameters:
    - page (int): Page number for pagination (default: 1, must be >= 1).
    - page_size (int): Number of consumers per page (default: 10, must be between 5 and 100).
    - sort_by (SortByEnum): Field used for sorting consumers (default: created_at).
    - order (OrderEnum): Sorting order, either ascending or descending (default: ascending).

    Returns:
    - PaginatedResponse: A structured response containing consumer data.
    """
    unit_of_work = UnitOfWork()

    return consumer_services.get_all_consumers(
        unit_of_work=unit_of_work,
        page=page,
        page_size=page_size,
        sort_by=sort_by.value,
        order=order.value,
    )


@router.get("/consumers/{consumer_id}", response_model=ConsumerDetailsResponse)
def get_consumer(consumer_id: UUID):
    """
    Fetches details of a registered consumer application.

    This endpoint retrieves the details of a specific consumer application using its unique identifier.

    Args:

        consumer_id (UUID):
            The unique identifier of the consumer application.

    Returns:

        ConsumerResponse:
            The details of the requested consumer application.

    Raises:

        HTTPException:
            If the consumer application is not found.
    """

    unit_of_work = UnitOfWork()

    return consumer_services.get_consumer_by_id(
        unit_of_work=unit_of_work,
        consumer_id=consumer_id,
    )


@router.post("/consumers/{consumer_id}/get-api", response_model=ApiKeyResponse)
def get_api_key(
    consumer_id: UUID,
    data: ApiKeyRequest,
):
    """
    Fetches the API key for a registered consumer application.

    This endpoint retrieves the API key associated with a specific consumer application using its unique identifier.

    Args:

        consumer_id (UUID):
            The unique identifier of the consumer application.

        data (ApiKeyRequest):
            The request payload containing the application secret and provider ID.

    Returns:

        ApiKeyResponse:
            The API key of the requested consumer application.

    Raises:

        HTTPException:
            If the consumer application is not found.
    """

    unit_of_work = UnitOfWork()

    return consumer_services.get_api_key(
        unit_of_work=unit_of_work,
        consumer_id=consumer_id,
        data=data,
    )


@router.patch("/consumers/{consumer_id}", response_model=Response)
def patch_consumer(consumer_id: UUID, data: ConsumerUpdateRequest):
    """
    Updates the details of a registered consumer application.

    This endpoint allows for partial updates to the details of a specific consumer application.

    Args:

        consumer_id (UUID):
            The unique identifier of the consumer application.

        data (ConsumerUpdateRequest):
            The request payload containing updated application details.

    Returns:

        ConsumerResponse:
            The updated details of the consumer application.

    Raises:

        HTTPException:
            If the consumer application is not found or if validation fails.
    """
    unit_of_work = UnitOfWork()

    return consumer_services.update_consumer(
        unit_of_work=unit_of_work,
        consumer_id=consumer_id,
        data=data,
    )


@router.delete("/consumers/{consumer_id}", status_code=204)
def delete_consumer(
    consumer_id: UUID,
):
    """
    Deletes a consumer from the database.

    Parameters:
        consumer_id (UUID):
            The unique identifier of the consumer to be deleted.

    Returns:
        Response:
            HTTP 204 No Content if deletion is successful.

    Raises:
        HTTPException 404: If the consumer with the given ID is not found.
    """
    unit_of_work = UnitOfWork()

    return consumer_services.delete_consumer(
        unit_of_work=unit_of_work,
        consumer_id=consumer_id,
    )
