from datetime import datetime, timezone
from uuid import UUID, uuid4

from cryptography.fernet import Fernet

from src.app.config.settings import app_config
from src.app.models.data_models import ApiKey, PermissionEnum, StatusEnum
from src.app.schemas.api_key_schema import APIKeyDetailResponse, APIKeyListResponse
from src.app.services.logging_service import log_activity
from src.app.services.unit_of_work import UnitOfWork


class APIKeyService:
    """
    Service class for managing API keys.

    Attributes:
        uow (UnitOfWork): Unit of work for API key operations.
        cipher_suite (Fernet): Cipher suite for encrypting API keys.
    """

    def __init__(self, uow: UnitOfWork):
        """
        Initializes the APIKeyService with a unit of work.

        Args:
            uow (UnitOfWork): Unit of work for API key operations.
        """
        self.uow = uow
        self.cipher_suite = Fernet(app_config["ENCRYPTION_KEY"])

    def validate_consumer_application(
        self, consumer_application_id: UUID, secret_hash: str
    ) -> None:
        """
        Validates the consumer application ID and secret hash.

        Args:
            consumer_application_id (UUID): The ID of the consumer application.
            secret_hash (str): The secret hash to validate.

        Raises:
            ValueError: If the consumer application ID or secret hash is invalid.
        """
        consumer_app = self.uow.application.get(consumer_application_id)
        if not consumer_app:
            raise ValueError("Invalid consumer application ID")

        if secret_hash != self.cipher_suite.decrypt(consumer_app.secret_hash).decode():
            raise ValueError("Invalid secret hash")

    def generate_api_key(
        self,
        consumer_application_id: UUID,
        provider_application_id: UUID,
        permissions: PermissionEnum,
        api_key_owner_id: UUID,
        expires_at: datetime,
        comment: str,
        secret_hash: str,
    ) -> dict:
        """
        Generates a new API key.

        Args:
            consumer_application_id (UUID): The ID of the consumer application.
            provider_application_id (UUID): The ID of the provider application.
            permissions (PermissionEnum): The permissions for the API key.
            api_key_owner_id (UUID): The ID of the API key owner.
            expires_at (datetime): The expiration date of the API key.
            comment (str): A comment for the API key.
            secret_hash (str): The secret hash for validation.

        Returns:
            dict: A dictionary containing the message, API key, and status.

        Raises:
            ValueError: If any validation fails.
        """

        with self.uow:
            error_messages = []

            try:
                self.validate_consumer_application(consumer_application_id, secret_hash)
            except ValueError as e:
                error_messages.append(str(e))

            provider_app = self.uow.application.get(provider_application_id)
            api_key_owner = self.uow.user.get(api_key_owner_id)
            consumer_app = self.uow.application.get(consumer_application_id)

            if not provider_app:
                error_messages.append("Invalid provider application ID")
            elif provider_app.type.value != "provider":
                error_messages.append(
                    "Application ID provided is not of type 'provider'"
                )

            if not consumer_app:
                error_messages.append("Invalid consumer application ID")
            elif consumer_app.type.value != "consumer":
                error_messages.append(
                    "Application ID provided is not of type 'consumer'"
                )

            if not api_key_owner:
                error_messages.append("Invalid user to be the owner")
            if permissions not in PermissionEnum.__members__.values():
                permissions = PermissionEnum.read
            if error_messages:
                raise ValueError(", ".join(error_messages))

            existing_api_keys, _ = self.uow.api_key.get_all(
                filters={
                    "provider_id": provider_application_id,
                    "consumer_id": consumer_application_id,
                }
            )
            existing_api_key = existing_api_keys[0] if existing_api_keys else None

            if existing_api_key:
                return {
                    "message": "API key for this provider ID and consumer ID is already available",
                    "api_key": existing_api_key.api_key,
                    "status": existing_api_key.status,
                }

            expires_at = expires_at.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            status = StatusEnum.active if expires_at >= now else StatusEnum.inactive
            api_key = str(uuid4())
            encrypted_api_key = self.cipher_suite.encrypt(api_key.encode())

            api_key_entry = ApiKey(
                provider_id=provider_application_id,
                consumer_id=consumer_application_id,
                api_key_owner_id=api_key_owner_id,
                permissions=permissions,
                api_key=encrypted_api_key.decode(),
                expires_at=expires_at,
                comment=comment,
                status=status,
                created_at=now,
                updated_at=None,
            )

            self.uow.api_key.add(api_key_entry)

            self.uow.commit()

            log_activity(
                unit_of_work=self.uow,
                application_id=consumer_application_id,
                description=f"API key created for consumer '{consumer_application_id}' and provider '{provider_application_id}' with permissions: {permissions}.",
            )

            return {
                "message": "API key generated successfully",
                "api_key": encrypted_api_key.decode(),
                "status": api_key_entry.status,
            }

    def get_all_api_keys(self, consumer_id: UUID, page: int = 1, page_size: int = 10):
        """
        Retrieves all API keys for a consumer with pagination.

        Args:
            consumer_id (UUID): The ID of the consumer.
            page (int): The page number for pagination. Defaults to 1.
            page_size (int): The number of items per page. Defaults to 10.

        Returns:
            APIKeyListResponse: A response object containing the API keys and pagination details.
        """
        with self.uow:
            api_keys, total = self.uow.api_key.get_all(
                page=page, page_size=page_size, filters={"consumer_id": consumer_id}
            )
            total_pages = (total + page_size - 1) // page_size
            previous_page = page - 1 if page > 1 else None
            next_page = page + 1 if page < total_pages else None
            api_key_responses = [
                APIKeyDetailResponse(**api_key.__dict__) for api_key in api_keys
            ]
            return APIKeyListResponse(
                total_pages=total_pages,
                previous_page=previous_page,
                current_page=page,
                next_page=next_page,
                page_size=page_size,
                items=api_key_responses,
            )

    def get_api_key(self, api_key_id: UUID):
        """
        Retrieves an API key by its ID.

        Args:
            api_key_id (UUID): The ID of the API key.

        Returns:
            APIKeyDetailResponse: The API key details if found, otherwise None.
        """
        with self.uow:
            api_key = self.uow.api_key.get(api_key_id)
            if api_key:
                return APIKeyDetailResponse(**api_key.__dict__)
            return None

    def update_api_key(self, api_key_id: UUID, **kwargs):
        """
        Updates an API key with provided attributes.

        Args:
            api_key_id (UUID): The ID of the API key to update.
            **kwargs (object): Attributes to update on the API key.

        Returns:
            dict: A message indicating the update status.
        """
        with self.uow:
            api_key = self.uow.api_key.get(api_key_id)

            if api_key.status == StatusEnum.revoked:
                print("DEBUG: API key is revoked. Skipping update.")
                return {
                    "message": f"API key with ID {api_key_id} is revoked. No updates are allowed."
                }

            if "expires_at" in kwargs:
                expires_at = kwargs["expires_at"].replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                if expires_at < now:
                    kwargs["status"] = StatusEnum.inactive
                else:
                    kwargs["status"] = StatusEnum.active

            print(f"DEBUG: Proceeding to update API key {api_key_id} with {kwargs}")
            self.uow.api_key.update(api_key_id, **kwargs)

            log_activity(
                unit_of_work=self.uow,
                application_id=api_key.consumer_id,
                description=f"API key '{api_key_id}' updated with details: {kwargs}.",
            )

            return {
                "message": f"API key with ID {api_key_id} has been updated successfully."
            }

    def delete_api_key(self, api_key_id: UUID):
        """
        Deletes an API key by its ID.

        Args:
            api_key_id (UUID): The ID of the API key to delete.

        Returns:
            dict: A message indicating the deletion status.
        """
        with self.uow:
            self.uow.api_key.delete(api_key_id)
            return {"message": "API key deleted successfully"}
