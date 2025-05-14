from datetime import datetime, timezone
from uuid import UUID, uuid4

from cryptography.fernet import Fernet

from src.app.config.settings import ENCRYPTION_KEY
from src.app.models.data_models import ApiKey, PermissionEnum, StatusEnum
from src.app.schemas.api_key_schema import (
    APIKeyDetailResponse,
    APIKeyListResponse,
    APIKeyResponse,
)
from src.app.services.unit_of_work import APIKeyUnitOfWork


class APIKeyService:
    def __init__(self, uow: APIKeyUnitOfWork, encryption_key: bytes):
        self.uow = uow
        self.cipher_suite = Fernet(encryption_key)

    def validate_consumer_application(
        self, consumer_application_id: UUID, secret_hash: str
    ) -> None:
        consumer_app = self.uow.application.get(consumer_application_id)
        if not consumer_app:
            raise ValueError("Invalid consumer application ID")

        if secret_hash != consumer_app.secret_hash:
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
        with self.uow:
            error_messages = []

            try:
                self.validate_consumer_application(consumer_application_id, secret_hash)
            except ValueError as e:
                error_messages.append(str(e))

            provider_app = self.uow.application.get(provider_application_id)
            api_key_owner = self.uow.user.get(api_key_owner_id)

            if not provider_app:
                error_messages.append("Invalid provider application ID")
            if not api_key_owner:
                error_messages.append("Invalid user to be the owner")
            if permissions not in PermissionEnum.__members__.values():
                permissions = PermissionEnum.read

            if error_messages:
                raise ValueError(", ".join(error_messages))

            existing_api_key = self.uow.api_key.get_by_provider_and_consumer(
                provider_id=provider_application_id, consumer_id=consumer_application_id
            )
            print(
                f"Fetched API key status: {existing_api_key.status if existing_api_key else 'None'}"
            )

            if existing_api_key:
                if existing_api_key.status in [StatusEnum.active, StatusEnum.revoked]:
                    return {
                        "message": "API key for this provider ID and consumer ID is already available",
                        "api_key": existing_api_key.api_key,
                        "status": existing_api_key.status,
                    }
                elif existing_api_key.status == StatusEnum.inactive:
                    existing_api_key.status = StatusEnum.revoked
                    print("Updating API key status to revoked")
                    self.uow.api_key.update(
                        existing_api_key.id,
                        **{
                            "status": StatusEnum.revoked,
                            "permissions": permissions,
                            "expires_at": expires_at,
                            "comment": comment,
                        },
                    )
                    print(f"API key updated: {existing_api_key}")
                    return {
                        "message": "API key details updated and status set to revoked",
                        "api_key": existing_api_key.api_key,
                        "status": existing_api_key.status,
                    }

            now = datetime.now(timezone.utc)
            is_active = now <= expires_at

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
                status=StatusEnum.active if is_active else StatusEnum.inactive,
                created_at=now,
                updated_at=None,
            )

            self.uow.api_key.add(api_key_entry)

            return {
                "message": "API key generated successfully",
                "api_key": encrypted_api_key.decode(),
                "status": api_key_entry.status,
            }

    def get_all_api_keys(self, consumer_id: UUID, page: int = 1, page_size: int = 10):
        with self.uow:
            api_keys, total = self.uow.api_key.get_all_by_consumer(
                consumer_id=consumer_id, page=page, page_size=page_size
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
        with self.uow:
            api_key = self.uow.api_key.get(api_key_id)
            if api_key:
                return APIKeyDetailResponse(**api_key.__dict__)
            return None

    def update_api_key(self, api_key_id: UUID, **kwargs):
        with self.uow:
            if "expires_at" in kwargs:
                expires_at = kwargs["expires_at"].replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                if expires_at < now:
                    kwargs["status"] = StatusEnum.inactive
            self.uow.api_key.update(api_key_id, **kwargs)
            return {
                "message": f"API key with ID {api_key_id} has been updated successfully."
            }

    def delete_api_key(self, api_key_id: UUID):
        with self.uow:
            self.uow.api_key.delete(api_key_id)
            return {"message": "API key deleted successfully"}
