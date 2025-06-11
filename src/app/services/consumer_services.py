from datetime import datetime, timedelta, timezone
from uuid import UUID

from cryptography.fernet import Fernet
from fastapi import HTTPException
from jose import jwt

from src.app.config.settings import app_config
from src.app.models.data_models import Consumer, StatusEnum, User
from src.app.schemas.api_key_schema import (
    APIKeyCreate,
    APIKeyDetailResponse,
    APIKeyListResponse,
    APIKeyResponse,
)
from src.app.services.unit_of_work import UnitOfWork

cipher_suite = Fernet(app_config["ENCRYPTION_KEY"])


class ConsumerService:
    """
    Service class for managing consumer-provider relationships and API keys.

    Attributes:
        uow (UnitOfWork): Unit of work for database operations.
    """

    def __init__(self):
        """
        Initializes the ConsumerService with a UnitOfWork instance.
        """
        self.uow = UnitOfWork()

    def _validate_consumer_secret(self, consumer_id: UUID, x_api_key: str):
        """
        Validates the consumer's secret key.

        Args:
            consumer_id (UUID): The ID of the consumer application.
            x_api_key (str): The API key provided for authentication.

        Raises:
            HTTPException: If the consumer application is not found, the secret cannot be decrypted,
                           or the API key is invalid.
        """
        with self.uow as uow:
            consumer_app = uow.application.get(id=consumer_id)
            if not consumer_app:
                raise HTTPException(
                    status_code=404, detail="Consumer application not found."
                )

            try:
                decrypted_secret = cipher_suite.decrypt(
                    consumer_app.secret_hash.encode()
                ).decode()
            except Exception:
                raise HTTPException(
                    status_code=400, detail="Failed to decrypt consumer secret."
                )

            if decrypted_secret != x_api_key:
                raise HTTPException(status_code=401, detail="Invalid x-api-key.")

    def _evaluate_status(self, consumer: Consumer) -> StatusEnum:
        """
        Evaluates the status of a consumer based on its expiration date.

        Args:
            consumer (Consumer): The consumer object.

        Returns:
            StatusEnum: The current status of the consumer.
        """
        now = datetime.now(timezone.utc)
        if consumer.expires_at and consumer.expires_at <= now:
            return StatusEnum.inactive
        return StatusEnum.active

    def create_relationship(
        self,
        provider_id: UUID,
        consumer_id: UUID,
        data: APIKeyCreate,
        x_api_key: str,
        current_user_id: UUID,
    ) -> dict:
        """
        Creates a relationship between a provider and a consumer.

        Args:
            provider_id (UUID): The ID of the provider application.
            consumer_id (UUID): The ID of the consumer application.
            data (APIKeyCreate): The API key creation details.
            x_api_key (str): The API key for authentication.
            current_user_id (UUID): The ID of the user creating the relationship.

        Returns:
            dict: A message indicating the result of the operation.

        Raises:
            HTTPException: If the provider, consumer, or user is invalid, or if the relationship already exists.
        """
        self._validate_consumer_secret(consumer_id, x_api_key)

        with self.uow as uow:
            provider = uow.application.get(id=provider_id)
            consumer = uow.application.get(id=consumer_id)
            owner = uow.user.get(id=current_user_id)

            if not owner:
                raise HTTPException(
                    status_code=404, detail="Invalid user id (owner_id)."
                )
            if not provider:
                raise HTTPException(status_code=404, detail="Invalid provider_id.")
            if not consumer:
                raise HTTPException(status_code=404, detail="Invalid consumer_id.")

            existing = uow.api_key.get(provider_id=provider_id, consumer_id=consumer_id)
            now = datetime.now(timezone.utc)

            if existing:
                if existing.status == StatusEnum.active:
                    raise HTTPException(
                        status_code=409, detail="Relationship already exists."
                    )

                new_status = (
                    StatusEnum.active if data.expires_at > now else StatusEnum.inactive
                )
                uow.api_key.update(
                    id=existing.id,
                    permissions=data.permissions,
                    expires_at=data.expires_at,
                    comment=data.comment,
                    updated_by=data.updated_by,
                    status=new_status,
                )
                return {"message": "Inactive relationship updated successfully."}

            status = StatusEnum.active if data.expires_at > now else StatusEnum.inactive
            consumer_record = Consumer(
                provider_id=provider_id,
                consumer_id=consumer_id,
                owner_id=current_user_id,
                permissions=data.permissions,
                status=status,
                expires_at=data.expires_at,
                comment=data.comment,
                created_by=data.created_by,
                updated_by=data.updated_by,
            )
            uow.api_key.add(consumer_record)

        return {"message": "Consumer relationship created successfully."}

    def generate_token(
        self,
        provider_id: UUID,
        consumer_id: UUID,
        x_api_key: str,
    ) -> APIKeyResponse:
        """
        Generates a token for a consumer-provider relationship.

        Args:
            provider_id (UUID): The ID of the provider application.
            consumer_id (UUID): The ID of the consumer application.
            x_api_key (str): The API key for authentication.

        Returns:
            APIKeyResponse: The generated token details.

        Raises:
            HTTPException: If the relationship is not found, inactive, or invalid.
        """
        self._validate_consumer_secret(consumer_id, x_api_key)

        with self.uow as uow:
            relationship = uow.api_key.get(
                provider_id=provider_id, consumer_id=consumer_id
            )
            if not relationship:
                raise HTTPException(
                    status_code=404,
                    detail="No relationship found between provider and consumer.",
                )

            current_status = self._evaluate_status(relationship)
            if current_status != relationship.status:
                uow.api_key.update(id=relationship.id, status=current_status)

            if current_status != StatusEnum.active:
                raise HTTPException(
                    status_code=403,
                    detail="No active relationship found. Please create a new one.",
                )

            permissions = relationship.permissions.value

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=int(app_config["ACCESS_TOKEN_EXPIRE_MINUTES"])
        )

        payload = {
            "provider_id": str(provider_id),
            "consumer_id": str(consumer_id),
            "permissions": permissions,
            "exp": expires_at,
        }

        token = jwt.encode(
            payload, app_config["SECRET_KEY"], algorithm=app_config["ALGORITHM"]
        )

        return APIKeyResponse(api_key=token, status=current_status)

    def get_consumer(
        self,
        provider_id: UUID,
        consumer_id: UUID,
        x_api_key: str,
    ) -> APIKeyDetailResponse:
        """
        Retrieves details of a consumer application.

        Args:
            provider_id (UUID): The ID of the provider application.
            consumer_id (UUID): The ID of the consumer application.
            x_api_key (str): The API key for authentication.

        Returns:
            APIKeyDetailResponse: The consumer application details.

        Raises:
            HTTPException: If the consumer is not found or the API key is invalid.
        """
        self._validate_consumer_secret(consumer_id, x_api_key)

        with self.uow as uow:
            consumer = uow.api_key.get(provider_id=provider_id, consumer_id=consumer_id)
            if not consumer:
                raise HTTPException(status_code=404, detail="Consumer not found.")

            current_status = self._evaluate_status(consumer)
            if current_status != consumer.status:
                uow.api_key.update(id=consumer.id, status=current_status)

            return APIKeyDetailResponse(
                id=consumer.id,
                provider_id=consumer.provider_id,
                consumer_id=consumer.consumer_id,
                api_key_owner_id=consumer.owner_id,
                permissions=consumer.permissions,
                expires_at=consumer.expires_at,
                comment=consumer.comment,
                status=current_status,
                created_at=consumer.created_at,
                updated_at=consumer.updated_at,
                created_by=consumer.created_by,
                updated_by=consumer.updated_by,
            )

    def get_all_consumers(
        self,
        provider_id: UUID,
        x_api_key: str,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        order: str = "asc",
    ) -> APIKeyListResponse:
        """
        Retrieves all consumers for a provider application with pagination.

        Args:
            provider_id (UUID): The ID of the provider application.
            x_api_key (str): The API key for authentication.
            page (int): The page number for pagination. Defaults to 1.
            page_size (int): The number of items per page. Defaults to 10.
            sort_by (str): The field to sort by. Defaults to "created_at".
            order (str): The sort order ("asc" or "desc"). Defaults to "asc".

        Returns:
            APIKeyListResponse: A paginated list of consumer details.

        Raises:
            HTTPException: If the provider is not found or the API key is invalid.
        """
        with self.uow as uow:
            provider_app = uow.application.get(id=provider_id)
            if not provider_app:
                raise HTTPException(
                    status_code=404, detail="Provider application not found."
                )

            try:
                decrypted_secret = cipher_suite.decrypt(
                    provider_app.secret_hash.encode()
                ).decode()
            except Exception:
                raise HTTPException(
                    status_code=400, detail="Failed to decrypt provider secret."
                )

            if decrypted_secret != x_api_key:
                raise HTTPException(
                    status_code=401, detail="Invalid x-api-key for provider."
                )

            consumers, total = uow.api_key.get_all(
                page=page,
                page_size=page_size,
                filters={"provider_id": provider_id},
                sort_by=sort_by,
                order_by=order,
            )

            items = []
            for c in consumers:
                current_status = self._evaluate_status(c)
                if current_status != c.status:
                    uow.api_key.update(id=c.id, status=current_status)

                items.append(
                    APIKeyDetailResponse(
                        id=c.id,
                        provider_id=c.provider_id,
                        consumer_id=c.consumer_id,
                        api_key_owner_id=c.owner_id,
                        permissions=c.permissions,
                        expires_at=c.expires_at,
                        comment=c.comment,
                        status=current_status,
                        created_at=c.created_at.date(),
                        updated_at=c.updated_at.date() if c.updated_at else None,
                        created_by=c.created_by,
                        updated_by=c.updated_by,
                    )
                )

            total_pages = (total + page_size - 1) // page_size
            return APIKeyListResponse(
                total_pages=total_pages,
                previous_page=page - 1 if page > 1 else None,
                current_page=page,
                next_page=page + 1 if page * page_size < total else None,
                page_size=page_size,
                items=[
                    APIKeyDetailResponse(
                        id=c.id,
                        provider_id=c.provider_id,
                        consumer_id=c.consumer_id,
                        api_key_owner_id=c.owner_id,
                        permissions=c.permissions,
                        expires_at=c.expires_at,
                        comment=c.comment,
                        status=self._evaluate_status(c),
                        created_at=c.created_at.date(),
                        updated_at=c.updated_at.date() if c.updated_at else None,
                        created_by=c.created_by,
                        updated_by=c.updated_by,
                    )
                    for c in consumers
                ],
            )
