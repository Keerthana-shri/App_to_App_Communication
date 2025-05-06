from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.app.repositories.base_repository import BaseRepository
from src.app.models.data_models import APIKey, PermissionEnum


class APIKeyRepository(BaseRepository[APIKey]):
    """
    A repository class for APIKey model.
    It provides methods to perform CRUD operations on APIKey data.
    """

    def get_all(
        self,
        consumer_application_id: Optional[UUID] = None,
        provider_application_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        permissions: Optional[PermissionEnum] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[APIKey]:
        query = self.session.query(APIKey)

        if consumer_application_id:
            query = query.filter(APIKey.consumer_application_id == consumer_application_id)
        if provider_application_id:
            query = query.filter(APIKey.provider_application_id == provider_application_id)
        if is_active is not None:
            query = query.filter(APIKey.is_active == is_active)
        if permissions:
            query = query.filter(APIKey.permissions == permissions)

        query = query.offset((page - 1) * page_size).limit(page_size)

        return query.all()

    def get(self, id: UUID) -> Optional[APIKey]:
        return self.session.query(APIKey).filter(APIKey.id == id).first()

    def add(self, **kwargs: object) -> None:
        api_key = APIKey(**kwargs)
        self.session.add(api_key)

    def update(self, id: UUID, **kwargs: object) -> None:
        api_key = self.get(id=id)
        if api_key:
            for key, value in kwargs.items():
                setattr(api_key, key, value)

    def delete(self, id: UUID) -> None:
        api_key = self.get(id=id)
        if api_key:
            self.session.delete(api_key)
