from datetime import datetime, timezone
from uuid import UUID

from cryptography.fernet import Fernet
from fastapi import HTTPException

from src.app.config.settings import app_config
from src.app.schemas.provider_schemas import (
    PaginatedResponse,
    ProviderDetailsResponse,
    ProviderRegisterRequest,
    ProviderUpdateRequest,
    Response,
)
from src.app.services.unit_of_work import UnitOfWork

ENCRYPTION_KEY = app_config["ENCRYPTION_KEY"]
cipher_suite = Fernet(ENCRYPTION_KEY)


def register_provider(unit_of_work: UnitOfWork, data: ProviderRegisterRequest):
    """
    Registers a provider application in the system.

    Args:
        unit_of_work (UnitOfWork): Database session and repository manager.
        data (ProviderRegisterRequest): Incoming request data for provider registration.

    Raises:
        HTTPException: If application data is already registered.

    Returns:
        dict: Confirmation message upon successful registration.
    """

    with unit_of_work as uow:
        # Check if the application is already registerd
        application = uow.application.get(id=data.application_guid)

        if application:
            raise HTTPException(
                status_code=409, detail="The application is already registered."
            )

        secret_code = str(data.application_secret)
        encrypted_secret = cipher_suite.encrypt(secret_code.encode()).decode()

        uow.application.add(
            id=data.application_guid,
            name=data.application_name,
            secret_hash=encrypted_secret,
            type="provider",
            user_id=data.user_id,
            comment=data.comments,
        )

    return {"message": "Application successfully registered."}


def get_all_providers(
    unit_of_work: UnitOfWork,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    order: str = "asc",
) -> list[ProviderDetailsResponse]:
    """
    Retrieves paginated provider applications with sorting.

    Args:
        unit_of_work (UnitOfWork): Manages database transactions.
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of records per page. Defaults to 10.
        sort_by (str, optional): Field used for sorting. Defaults to "created_at".
            - Expected values: "name", "status", "created_at", "updated_at"
        order (str, optional): Sorting order. Defaults to "asc".
            - Expected values: "asc", "desc"

    Returns:
        list[ProviderDetailsResponse]: Paginated list of provider applications.
            - Includes metadata such as total pages, previous/next pages, and page size.
    """
    with unit_of_work as uow:
        # Fetch all provider applications
        providers = uow.application.get_all(
            type="provider", sort_by=sort_by, order=order
        )

        formatted_providers = [
            ProviderDetailsResponse(
                id=provider.id,
                name=provider.name,
                status=provider.status.value,
                user_id=provider.user_id,
                comment=provider.comment,
                created_at=provider.created_at.replace(
                    tzinfo=timezone.utc
                ).astimezone(),
                updated_at=(
                    provider.updated_at.replace(tzinfo=timezone.utc).astimezone()
                    if provider.updated_at and provider.updated_at.tzinfo is None
                    else provider.updated_at
                ),
            )
            for provider in providers
        ]

        # Paginate logic
        total = len(formatted_providers)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_items = formatted_providers[start_index:end_index]

        paginated_response = PaginatedResponse(
            total_pages=(total + page_size - 1) // page_size,
            previous_page=page - 1 if page > 1 else None,
            current_page=page,
            next_page=page + 1 if end_index < total else None,
            page_size=page_size,
            items=paginated_items,
        )

    return paginated_response


def get_provider_by_id(unit_of_work: UnitOfWork, provider_id: UUID):
    """
    Retrieves a provider application by its unique identifier.

    Args:
        unit_of_work (UnitOfWork): Database session and repository manager.
        provider_id (UUID): Unique identifier of the provider application.

    Raises:
        HTTPException: If the provider application is not found.

    Returns:
        dict: Details of the requested provider application.
    """

    with unit_of_work as uow:
        # Fetch the provider application by ID
        provider = uow.application.get(id=provider_id)

        if not provider:
            raise HTTPException(
                status_code=404, detail="Provider application not found."
            )

        # Check if the application is a provider
        if provider.type.value != "provider":
            raise HTTPException(
                status_code=403, detail="Cannot access a non-provider application."
            )

        provider = ProviderDetailsResponse(
            id=provider.id,
            name=provider.name,
            status=provider.status.value,
            user_id=provider.user_id,
            comment=provider.comment,
            created_at=provider.created_at,
            updated_at=provider.updated_at,
        )

    return provider


def update_provider(
    unit_of_work: UnitOfWork, provider_id: UUID, data: ProviderUpdateRequest
) -> Response:
    """Partially updates provider details."""

    with unit_of_work as uow:
        # Fetch the provider application by ID
        provider = uow.application.get(id=provider_id)
        if not provider:
            raise HTTPException(
                status_code=404, detail="Provider application not found."
            )

        # Check if the application is a provider
        if provider.type.value != "provider":
            raise HTTPException(
                status_code=403, detail="Cannot update a non-provider application."
            )

        # Update only fields that are provided
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        uow.application.update(provider_id, **update_data)

        return {"message": "Application successfully updated."}


def delete_provider(unit_of_work: UnitOfWork, provider_id: UUID) -> Response:
    """Deletes a provider application."""

    with unit_of_work as uow:
        # Fetch the provider application by ID
        provider = uow.application.get(id=provider_id)
        if not provider:
            raise HTTPException(
                status_code=404, detail="Provider application not found."
            )

        # Check if the application is a provider
        if provider.type.value != "provider":
            raise HTTPException(
                status_code=403, detail="Cannot delete a non-provider application."
            )

        uow.application.delete(provider_id)

        return {"message": "Application successfully deleted."}
