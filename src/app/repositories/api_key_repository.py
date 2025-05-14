from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.app.models.data_models import ApiKey, StatusEnum


class APIKeyRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self, page: int = 1, page_size: int = 10) -> Tuple[List[ApiKey], int]:
        skip = (page - 1) * page_size
        query = self.session.query(ApiKey)
        total = query.count()
        api_keys = query.offset(skip).limit(page_size).all()
        return api_keys, total

    def get_all_by_consumer(
        self, consumer_id: UUID, page: int = 1, page_size: int = 10
    ) -> Tuple[List[ApiKey], int]:
        skip = (page - 1) * page_size
        query = self.session.query(ApiKey).filter(ApiKey.consumer_id == consumer_id)
        total = query.count()
        api_keys = query.offset(skip).limit(page_size).all()
        return api_keys, total

    def get(self, id: UUID) -> Optional[ApiKey]:
        return self.session.query(ApiKey).filter(ApiKey.id == id).first()

    def get_by_provider_and_consumer(
        self, provider_id: UUID, consumer_id: UUID
    ) -> Optional[ApiKey]:
        api_key = (
            self.session.query(ApiKey)
            .filter(
                ApiKey.provider_id == provider_id, ApiKey.consumer_id == consumer_id
            )
            .first()
        )
        print(
            f"Inside get_by_provider_and_consumer: Fetched API key status: {api_key.status if api_key else 'None'}"
        )
        return api_key

    def add(self, api_key: ApiKey) -> None:
        self.session.add(api_key)

    def update(self, id: UUID, **kwargs: object) -> None:
        api_key = self.get(id=id)
        if api_key:
            allowed_fields = {
                "status",
                "permissions",
                "expires_at",
                "comment",
                "api_key",
            }
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(api_key, key, value)
            api_key.updated_at = datetime.now(timezone.utc)
            if "expires_at" in kwargs:
                expires_at = kwargs["expires_at"].replace(tzinfo=timezone.utc)
                if expires_at < api_key.updated_at:
                    api_key.status = StatusEnum.inactive

    def delete(self, id: UUID) -> None:
        api_key = self.get(id=id)
        if api_key:
            self.session.delete(api_key)
