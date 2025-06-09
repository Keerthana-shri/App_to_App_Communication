from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from src.app.schemas.auth_schemas import UserRegisterResponse
from src.app.schemas.provider_schemas import (
    OrderEnum,
    PaginatedResponse,
    ProviderDetailsResponse,
    ProviderRegisterRequest,
    ProviderUpdateRequest,
    Response,
    SortByEnum,
)
from src.app.services.application_services import ApplicationService
from src.app.services.auth_services import AuthService

router = APIRouter(tags=["Application"])
service = ApplicationService()
auth_service = AuthService()


@router.post("/applications", response_model=Response, status_code=201)
def register_provider(
    data: ProviderRegisterRequest,
    current_user: UserRegisterResponse = Depends(auth_service.get_current_user),
):
    """
    **Registers a provider application.**

    This endpoint handles the registration of a provider application. It validates the provided application details, ensures no duplicate registration, and securely stores relevant information.

    **Parameters**:

        data (ProviderRegisterRequest):
            The request payload containing application details.

        current_user (UserRegisterResponse):
            The currently authenticated user, used for authorization.

    **Returns**:

        ProviderRegisterResponse:
            The response confirming successful registration.

    **Raises**:

        HTTPException:
            If validation fails or the application is already registered.
    """
    return service.register(
        data=data,
        current_user=current_user,
    )


@router.get("/applications", response_model=PaginatedResponse)
def get_all_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=5, le=100),
    sort_by: SortByEnum = Query(SortByEnum.created_at),
    order: OrderEnum = Query(OrderEnum.asc),
    current_user: UserRegisterResponse = Depends(auth_service.get_current_user),
):
    """
    **Retrieve a paginated list of applications.**

    This endpoint fetches a list of applications with optional pagination, sorting, and ordering.

    **Parameters**:

        page (int):
            Page number for pagination (default: 1, must be >= 1).

        page_size (int):
            Number of applications per page (default: 10, must be between 5 and 100).

        sort_by (SortByEnum):
            Field used for sorting applications (default: created_at).

        order (OrderEnum):
            Sorting order, either ascending or descending (default: ascending).

        current_user (UserRegisterResponse):
            The currently authenticated user, used for authorization.

    **Returns**:

        PaginatedResponse:
            A structured response containing provider data.
    """
    return service.get_all(
        page=page,
        page_size=page_size,
        sort_by=sort_by.value,
        order=order.value,
        current_user=current_user,
    )


@router.get("/applications/{provider_id}", response_model=ProviderDetailsResponse)
def get_provider(
    provider_id: UUID = Path(
        ..., description="The unique identifier of the provider application."
    ),
    current_user: UserRegisterResponse = Depends(auth_service.get_current_user),
):
    """
    **Fetches details of a registered provider application.**

    This endpoint retrieves the details of a specific provider application using its unique identifier.

    **Parameters**:

        provider_id (UUID):
            The unique identifier of the provider application.

        current_user (UserRegisterResponse):
            The currently authenticated user, used for authorization.

    **Returns**:

        ProviderDetailsResponse:
            The details of the requested provider application.

    **Raises**:

        HTTPException:
            If the provider application is not found.
    """

    return service.get_one(
        provider_id=provider_id,
        current_user=current_user,
    )


@router.patch("/applications/{provider_id}", response_model=Response)
def patch_provider(
    provider_id: UUID,
    data: ProviderUpdateRequest,
    current_user: UserRegisterResponse = Depends(auth_service.get_current_user),
):
    """
    **Updates the details of a registered provider application.**

    This endpoint allows for partial updates to the details of a specific provider application.

    **Parameters**:

        provider_id (UUID):
            The unique identifier of the provider application.

        data (ProviderUpdateRequest):
            The request payload containing updated application details.

        current_user (UserRegisterResponse):
            The currently authenticated user, used for authorization.

    **Returns**:

        Response:
            The updated details of the provider application.

    **Raises**:

        HTTPException:
            If the provider application is not found or if validation fails.
    """
    return service.update(
        provider_id=provider_id,
        data=data,
        current_user=current_user,
    )


@router.delete("/applications/{provider_id}", status_code=204)
def delete_provider(
    provider_id: UUID,
    current_user: UserRegisterResponse = Depends(auth_service.get_current_user),
):
    """
    **Deletes a provider from the database.**

    **Parameters**:

        provider_id (UUID):
            The unique identifier of the provider to be deleted.

        current_user (UserRegisterResponse):
            The currently authenticated user, used for authorization.

    **Returns**:

        Response:
            HTTP 204 No Content if deletion is successful.

    **Raises**:

        HTTPException 404:
            If the provider with the given ID is not found.
    """
    return service.delete(
        provider_id=provider_id,
        current_user=current_user,
    )
