from datetime import datetime, timezone
from uuid import UUID

from cryptography.fernet import Fernet
from fastapi import HTTPException

from src.app.config.settings import app_config
from src.app.schemas.consumer_schemas import (
    ApiKeyRequest,
    ApiKeyResponse,
    ConsumerDetailsResponse,
    ConsumerRegisterRequest,
    ConsumerUpdateRequest,
    PaginatedResponse,
    Response,
)
from src.app.services.logging_service import log_activity
from src.app.services.unit_of_work import UnitOfWork

ENCRYPTION_KEY = app_config["ENCRYPTION_KEY"]
cipher_suite = Fernet(ENCRYPTION_KEY)


def register_consumer(unit_of_work: UnitOfWork, data: ConsumerRegisterRequest):
    """
    Registers a consumer application in the system.

    Args:
        unit_of_work (UnitOfWork): Database session and repository manager.
        data (ConsumerRegisterRequest): Incoming request data for consumer registration.

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

        # Hash the application secret using bcrypt
        secret_code = str(data.application_secret)
        encrypted_secret = cipher_suite.encrypt(secret_code.encode()).decode()

        uow.application.add(
            id=data.application_guid,
            name=data.application_name,
            secret_hash=encrypted_secret,
            type="consumer",
            user_id=data.user_id,
            comment=data.comments,
        )

        uow.session.commit()

        log_activity(
            unit_of_work=uow,
            application_id=data.application_guid,
            description=f"Consumer application '{data.application_name}' registered with details: {data.dict()}",
        )

    return {"message": "Application successfully registered."}


def get_all_consumers(
    unit_of_work: UnitOfWork,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    order: str = "asc",
) -> list[ConsumerDetailsResponse]:
    """
    Retrieves paginated consumer applications with sorting.

    Args:
        unit_of_work (UnitOfWork): Manages database transactions.
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of records per page. Defaults to 10.
        sort_by (str, optional): Field used for sorting. Defaults to "created_at".
            - Expected values: "name", "status", "created_at", "updated_at"
        order (str, optional): Sorting order. Defaults to "asc".
            - Expected values: "asc", "desc"

    Returns:
        list[ConsumerDetailsResponse]: Paginated list of consumer applications.
            - Includes metadata such as total pages, previous/next pages, and page size.
    """
    with unit_of_work as uow:
        # Fetch all consumer applications
        consumers = uow.application.get_all(
            type="consumer", sort_by=sort_by, order=order
        )

        formatted_consumers = [
            ConsumerDetailsResponse(
                id=consumer.id,
                name=consumer.name,
                status=consumer.status.value,
                user_id=consumer.user_id,
                comment=consumer.comment,
                created_at=consumer.created_at,
                updated_at=consumer.updated_at,
            )
            for consumer in consumers
        ]

        # Paginate logic
        total = len(formatted_consumers)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_items = formatted_consumers[start_index:end_index]

        paginated_response = PaginatedResponse(
            total_pages=(total + page_size - 1) // page_size,
            previous_page=page - 1 if page > 1 else None,
            current_page=page,
            next_page=page + 1 if end_index < total else None,
            page_size=page_size,
            items=paginated_items,
        )

    return paginated_response


def get_consumer_by_id(unit_of_work: UnitOfWork, consumer_id: UUID):
    """
    Retrieves a consumer application by its unique identifier.

    Args:
        unit_of_work (UnitOfWork): Database session and repository manager.
        consumer_id (UUID): Unique identifier of the consumer application.

    Raises:
        HTTPException: If the consumer application is not found.

    Returns:
        dict: Details of the requested consumer application.
    """

    with unit_of_work as uow:
        # Fetch the consumer application by ID
        consumer = uow.application.get(id=consumer_id)

        if not consumer:
            raise HTTPException(
                status_code=404, detail="Consumer application not found."
            )

        # Check if the application is a consumer
        if consumer.type.value != "consumer":
            raise HTTPException(
                status_code=403, detail="Cannot access a non-consumer application."
            )

        consumer = ConsumerDetailsResponse(
            id=consumer.id,
            name=consumer.name,
            status=consumer.status.value,
            user_id=consumer.user_id,
            comment=consumer.comment,
            created_at=consumer.created_at,
            updated_at=consumer.updated_at,
        )

    return consumer


def get_api_key(
    unit_of_work: UnitOfWork, consumer_id: UUID, data: ApiKeyRequest
) -> ApiKeyResponse:
    """
    Retrieves an API key for a consumer application interacting with a provider application.

    Args:
        unit_of_work (UnitOfWork): The database transaction handler.
        consumer_id (UUID): The unique identifier of the consumer application.
        data (ApiKeyRequest): Request body containing the provider ID and application secret.

    Returns:
        ApiKeyResponse: Contains the API key if validation succeeds.

    Raises:
        HTTPException: If the consumer application is not found (404).
        HTTPException: If the application type is not "consumer" (403).
        HTTPException: If the provided application secret is invalid (403).
        HTTPException: If the provider application is not found (404).
        HTTPException: If the provider type is not "provider" (403).
        HTTPException: If the API key does not exist (404).
        HTTPException: If the API key is inactive (403).
        HTTPException: If the API key has been revoked (403).
    """
    with unit_of_work as uow:
        # Fetch the consumer application by ID
        consumer = uow.application.get(id=consumer_id)

        if not consumer:
            raise HTTPException(
                status_code=404, detail="Consumer application not found."
            )

        # Check if the application is a consumer
        if consumer.type.value != "consumer":
            raise HTTPException(
                status_code=403, detail="Cannot access a non-consumer application."
            )

        if (
            str(data.application_secret)
            != cipher_suite.decrypt(consumer.secret_hash).decode()
        ):
            raise HTTPException(status_code=403, detail="Invalid application secret.")

        # Check if the provider application exists
        provider = uow.application.get(id=data.provider_id)
        if not provider:
            raise HTTPException(
                status_code=404, detail="Provider application not found."
            )

        # Check if the provider application is of type "provider"
        if provider.type.value != "provider":
            raise HTTPException(
                status_code=403,
                detail="Given provider id is not registered as provider.",
            )

        api_key_record = uow.api_key.get(
            consumer_id=consumer.id,
            provider_id=provider.id,
        )

        # Check if the API key exists for the given consumer and provider
        if not api_key_record:
            raise HTTPException(
                status_code=404,
                detail="API key not found for the given consumer and provider.",
            )

        # Check if the API key is active
        if api_key_record.status.value == "inactive":
            raise HTTPException(status_code=403, detail="API key is not active.")

        # Check if the API key is revoked
        if api_key_record.status.value == "revoked":
            raise HTTPException(status_code=403, detail="API key has been revoked.")

        api_key = ApiKeyResponse(x_api_key=api_key_record.api_key)

    return api_key


def update_consumer(
    unit_of_work: UnitOfWork, consumer_id: UUID, data: ConsumerUpdateRequest
) -> Response:
    """Partially updates consumer details."""

    with unit_of_work as uow:
        # Fetch the consumer application by ID
        consumer = uow.application.get(id=consumer_id)
        if not consumer:
            raise HTTPException(
                status_code=404, detail="Consumer application not found."
            )

        # Check if the application is a consumer
        if consumer.type.value != "consumer":
            raise HTTPException(
                status_code=403, detail="Cannot update a non-consumer application."
            )

        # Update only fields that are provided
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        uow.application.update(consumer_id, **update_data)

        log_activity(
            unit_of_work=uow,
            application_id=consumer_id,
            description=f"Consumer application '{consumer.name}' updated with details: {update_data}",
        )

        return {"message": "Application successfully updated."}


def delete_consumer(unit_of_work: UnitOfWork, consumer_id: UUID) -> Response:
    """Deletes a consumer application."""

    with unit_of_work as uow:
        # Fetch the consumer application by ID
        consumer = uow.application.get(id=consumer_id)
        if not consumer:
            raise HTTPException(
                status_code=404, detail="Consumer application not found."
            )

        # Check if the application is a consumer
        if consumer.type.value != "consumer":
            raise HTTPException(
                status_code=403, detail="Cannot delete a non-consumer application."
            )

        uow.application.delete(consumer_id)

        log_activity(
            unit_of_work=uow,
            application_id=consumer_id,
            description=f"Consumer application '{consumer.name}' deleted.",
        )

        return {"message": "Application successfully deleted."}
