from uuid import UUID

from fastapi import APIRouter, Query

import src.app.services.provider_services as provider_services
from src.app.schemas.provider_schemas import (
    OrderEnum,
    PaginatedResponse,
    ProviderDetailsResponse,
    ProviderRegisterRequest,
    ProviderUpdateRequest,
    Response,
    SortByEnum,
)
from src.app.services.unit_of_work import UnitOfWork

router = APIRouter(tags=["Provider"])


@router.post("/providers", response_model=Response, status_code=201)
def register_provider(data: ProviderRegisterRequest):
    """Registers a provider application.

    This endpoint handles the registration of a provider application. It validates the provided application details, ensures no duplicate registration, and securely stores relevant information.

    Args:

        data (ProviderRegisterRequest):
            The request payload containing application details.

    Returns:

        ProviderRegisterResponse:
            The response confirming successful registration.

    Raises:

        HTTPException:
            If validation fails or the application is already registered.
    """

    unit_of_work = UnitOfWork()
    return provider_services.register_provider(
        unit_of_work=unit_of_work,
        data=data,
    )


@router.get("/providers", response_model=PaginatedResponse)
def get_all_providers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=5, le=100),
    sort_by: SortByEnum = Query(SortByEnum.created_at),
    order: OrderEnum = Query(OrderEnum.asc),
):
    unit_of_work = UnitOfWork()

    return provider_services.get_all_providers(
        unit_of_work=unit_of_work,
        page=page,
        page_size=page_size,
        sort_by=sort_by.value,
        order=order.value,
    )


@router.get("/providers/{provider_id}", response_model=ProviderDetailsResponse)
def get_provider(provider_id: UUID):
    """
    Fetches details of a registered provider application.

    This endpoint retrieves the details of a specific provider application using its unique identifier.

    Args:

        provider_id (UUID):
            The unique identifier of the provider application.

    Returns:

        ProviderResponse:
            The details of the requested provider application.

    Raises:

        HTTPException:
            If the provider application is not found.
    """

    unit_of_work = UnitOfWork()

    return provider_services.get_provider_by_id(
        unit_of_work=unit_of_work,
        provider_id=provider_id,
    )


@router.patch("/providers/{provider_id}", response_model=Response)
def patch_provider(provider_id: UUID, data: ProviderUpdateRequest):
    """
    Updates the details of a registered provider application.

    This endpoint allows for partial updates to the details of a specific provider application.

    Args:

        provider_id (UUID):
            The unique identifier of the provider application.

        data (ProviderUpdateRequest):
            The request payload containing updated application details.

    Returns:

        ProviderResponse:
            The updated details of the provider application.

    Raises:

        HTTPException:
            If the provider application is not found or if validation fails.
    """
    unit_of_work = UnitOfWork()

    return provider_services.update_provider(
        unit_of_work=unit_of_work,
        provider_id=provider_id,
        data=data,
    )


@router.delete("/providers/{provider_id}", status_code=204)
def delete_provider(
    provider_id: UUID,
):
    """
    Deletes a provider from the database.

    Parameters:
        provider_id (UUID):
            The unique identifier of the provider to be deleted.

    Returns:
        Response:
            HTTP 204 No Content if deletion is successful.

    Raises:
        HTTPException 404: If the provider with the given ID is not found.
    """
    unit_of_work = UnitOfWork()

    return provider_services.delete_provider(
        unit_of_work=unit_of_work,
        provider_id=provider_id,
    )
