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

    def get(self, id: UUID) -> Optional[ApiKey]:
        return self.session.query(ApiKey).filter(ApiKey.id == id).first()

    def add(self, api_key: ApiKey) -> None:
        self.session.add(api_key)

    def update(self, id: UUID, **kwargs: object) -> None:
        """
        Update an existing API key with new attributes.

        Args:
            id (UUID): The unique identifier of the API key to update.
            **kwargs (object): The attributes to update.

        Returns:
            None
        """
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
        """
        Delete an API key from the database.

        Args:
            id (UUID): The unique identifier of the API key to delete.

        Returns:
            None
        """
        api_key = self.get(id=id)
        if api_key:
            self.session.delete(api_key)