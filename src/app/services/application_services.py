from datetime import datetime, timezone
from uuid import UUID

from cryptography.fernet import Fernet
from fastapi import HTTPException

from src.app.config.settings import app_config
from src.app.schemas.auth_schemas import TokenInfo, UserRegisterResponse
from src.app.schemas.provider_schemas import (
    OrderEnum,
    PaginatedResponse,
    ProviderDetailsResponse,
    ProviderRegisterRequest,
    ProviderUpdateRequest,
    Response,
    SortByEnum,
)
from src.app.services.logging_service import log_activity
from src.app.services.unit_of_work import UnitOfWork

ENCRYPTION_KEY = app_config["ENCRYPTION_KEY"]
cipher_suite = Fernet(ENCRYPTION_KEY)


class ApplicationService:
    """
    Service for handling application-related operations.
    """

    def __init__(self):
        self.uow = UnitOfWork()

    def register(self, data: ProviderRegisterRequest, current_user: TokenInfo) -> dict:
        """
        Registers a applications application in the system.

        Args:
            data (ProviderRegisterRequest): Incoming request data for applications registration.
            current_user (TokenInfo): The currently authenticated user, used for authorization.

        Raises:
            HTTPException: If application data is already registered.

        Returns:
            dict: Confirmation message upon successful registration.
        """

        with self.uow as uow:
            # Check if the application is already registerd
            application = uow.application.get(id=data.application_guid)

            if application:
                raise HTTPException(
                    status_code=409, detail="The application is already registered."
                )

            user = uow.user.get(id=data.user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")

            secret_code = str(data.application_secret)
            encrypted_secret = cipher_suite.encrypt(secret_code.encode()).decode()

            uow.application.add(
                id=data.application_guid,
                name=data.application_name,
                secret_hash=encrypted_secret,
                type="provider",
                owner_id=data.user_id,
                created_by=current_user.id,
                comment=data.comments,
            )

        with self.uow as uow:
            log_activity(
                unit_of_work=uow,
                application_id=data.application_guid,
                description=f"Provider application '{data.application_name}' registered with details: {data.dict()}",
            )

        return {"message": "Application successfully registered."}

    def get_all(
        self,
        page: int,
        page_size: int,
        sort_by: SortByEnum,
        order: OrderEnum,
        current_user: UserRegisterResponse,
    ) -> PaginatedResponse:
        """
        Retrieves a paginated list of applications.

        Args:
            page (int): The page number to retrieve.
            page_size (int): The number of items per page.
            sort_by (SortByEnum): The field to sort by.
            order (OrderEnum): The order of sorting (ascending or descending).
            current_user (UserRegisterResponse): The currently authenticated user.

        Returns:
            PaginatedResponse: A paginated response containing the list of applications.
        """
        with self.uow as uow:
            providers = uow.application.get_all(
                type="provider", sort_by=sort_by, order=order
            )

            formatted_providers = [
                ProviderDetailsResponse(
                    id=provider.id,
                    name=provider.name,
                    status=provider.status.value,
                    owner_id=provider.owner_id,
                    comment=provider.comment,
                    created_at=provider.created_at.replace(
                        tzinfo=timezone.utc
                    ).astimezone(),
                    updated_at=(
                        provider.updated_at.replace(tzinfo=timezone.utc).astimezone()
                        if provider.updated_at and provider.updated_at.tzinfo is None
                        else provider.updated_at
                    ),
                    created_by=provider.created_by,
                    updated_by=provider.updated_by,
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

    def get_one(
        self,
        provider_id: UUID,
        current_user: UserRegisterResponse,
    ) -> ProviderDetailsResponse:
        """
        Retrieves details of a specific provider application by its ID.

        Args:
            provider_id (UUID): The unique identifier of the provider application.
            current_user (UserRegisterResponse): The currently authenticated user.

        Returns:
            ProviderDetailsResponse: The details of the specified provider application.

        Raises:
            HTTPException: If the provider application is not found.
        """
        with self.uow as uow:
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
                owner_id=provider.owner_id,
                comment=provider.comment,
                created_at=provider.created_at,
                updated_at=provider.updated_at,
                created_by=provider.created_by,
                updated_by=provider.updated_by,
            )

        return provider

    def update(
        self,
        provider_id: UUID,
        data: ProviderUpdateRequest,
        current_user: UserRegisterResponse,
    ) -> Response:
        """
        Updates the details of a specific provider application.

        Args:
            provider_id (UUID): The unique identifier of the provider application.
            data (ProviderUpdateRequest): The request payload containing updated application details.
            current_user (UserRegisterResponse): The currently authenticated user.

        Returns:
            Response: Confirmation message upon successful update.

        Raises:
            HTTPException: If the provider application is not found or if the update fails.
        """
        with self.uow as uow:
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
            update_data["updated_by"] = current_user.id
            uow.application.update(provider_id, **update_data)

        with self.uow as uow:
            # Fetch the provider application by ID
            provider = uow.application.get(id=provider_id)
            log_activity(
                unit_of_work=uow,
                application_id=provider_id,
                description=f"Provider application '{provider.name}' updated with details: {update_data} by {current_user.id}",
            )

        return Response(message="Application successfully updated.")

    def delete(
        self,
        provider_id: UUID,
        current_user: UserRegisterResponse,
    ) -> Response:
        """
        Deletes a provider application.

        Args:
            provider_id (UUID): The unique identifier of the provider application.
            current_user (UserRegisterResponse): The currently authenticated user.

        Returns:
            Response: Confirmation message upon successful deletion.

        Raises:
            HTTPException: If the provider application is not found or if the deletion fails.
        """
        provider_name = ""
        with self.uow as uow:
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
            provider_name = provider.name
            uow.application.delete(provider_id)

        with self.uow as uow:
            log_activity(
                unit_of_work=uow,
                description=f"Provider application '{provider_name}' deleted by {current_user.id}.",
            )

        return Response(message="Application successfully deleted.")
