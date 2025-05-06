from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.app.models.data_models import APIKey, PermissionEnum
from src.app.services.unit_of_work import APIKeyUnitOfWork


class APIKeyService:
    def __init__(self, uow: APIKeyUnitOfWork):
        self.uow = uow

    def generate_api_key(
        self,
        consumer_name: str,
        consumer_application_id: UUID,
        provider_name: str,
        provider_application_id: UUID,
        permissions: PermissionEnum,
        api_key_owner: UUID,
        expires_at: datetime,
        comment: str,
        secret_hash: str,
    ) -> dict:
        try:
            with self.uow:
                consumer_provider = self.uow.provider.get(consumer_application_id)
                if (
                    not consumer_provider
                    or consumer_provider.secret_hash != secret_hash
                ):
                    return {"error": "Invalid consumer application ID or secret hash"}

                provider_application = self.uow.provider.get(provider_application_id)
                if not provider_application:
                    return {"error": "Invalid provider application ID"}

                now = datetime.now(timezone.utc)

                is_active = now <= expires_at

                api_key = str(uuid4())

                api_key_entry = APIKey(
                    consumer_application_id=consumer_application_id,
                    consumer_name=consumer_name,
                    api_key=api_key,
                    provider_application_id=provider_application_id,
                    provider_name=provider_name,
                    permissions=permissions,
                    api_key_owner=api_key_owner,
                    is_active=is_active,
                    created_at=now,
                    expires_at=expires_at,
                    comment=comment,
                )

                api_key_data = {
                    key: value
                    for key, value in api_key_entry.__dict__.items()
                    if key != "_sa_instance_state"
                }

                self.uow.api_key.add(**api_key_data)

                return {"message": "API key generated successfully", "api_key": api_key}
        except Exception as e:
            return {"error": str(e)}
