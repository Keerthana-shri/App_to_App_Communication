from typing import List, Optional
from uuid import UUID

from src.app.repositories.base_repository import BaseRepository
from src.app.models.data_models import ApiKey, PermissionEnum


class APIKeyRepository(BaseRepository[ApiKey]):
    """
    A repository class for ApiKey model.
    It provides methods to perform CRUD operations on ApiKey data.
    """

    def get_all(
        self,
        consumer_application_id: Optional[UUID] = None,
        provider_application_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        permissions: Optional[PermissionEnum] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[ApiKey]:
        """
        Retrieve a paginated list of API keys based on the provided filters.

        Args:
            consumer_application_id (Optional[UUID]): Filter by consumer application ID.
            provider_application_id (Optional[UUID]): Filter by provider application ID.
            is_active (Optional[bool]): Filter by active status.
            permissions (Optional[PermissionEnum]): Filter by permissions.
            page (int): The page number for pagination (default is 1).
            page_size (int): The number of items per page (default is 10).

        Returns:
            List[ApiKey]: A list of ApiKey objects matching the filters.
        """
        query = self.session.query(ApiKey)

        if consumer_application_id:
            query = query.filter(ApiKey.consumer_application_id == consumer_application_id)
        if provider_application_id:
            query = query.filter(ApiKey.provider_application_id == provider_application_id)
        if is_active is not None:
            query = query.filter(ApiKey.is_active == is_active)
        if permissions:
            query = query.filter(ApiKey.permissions == permissions)

        query = query.offset((page - 1) * page_size).limit(page_size)

        return query.all()

    def get(self, id: UUID) -> Optional[ApiKey]:
        """
        Retrieve a single API key by its ID.

        Args:
            id (UUID): The unique identifier of the API key.

        Returns:
            Optional[ApiKey]: The ApiKey object if found, otherwise None.
        """
        return self.session.query(ApiKey).filter(ApiKey.id == id).first()

    def get_by_key(self, key: str) -> Optional[ApiKey]:
        """
        Retrieve an API key by its key value.

        Args:
            key (str): The API key value.

        Returns:
            Optional[ApiKey]: The ApiKey object if found, otherwise None.
        """
        return self.session.query(ApiKey).filter(ApiKey.api_key == key).first()

    def add(self, **kwargs: object) -> None:
        """
        Add a new API key to the database.

        Args:
            **kwargs (object): The attributes of the API key to be created.

        Returns:
            None
        """
        api_key = ApiKey(**kwargs)
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
            for key, value in kwargs.items():
                setattr(api_key, key, value)

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