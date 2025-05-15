from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.app.models.data_models import ApiKey, StatusEnum


class APIKeyRepository:
    """
    Repository class for managing API keys in the database.

    Attributes:
        session (Session): SQLAlchemy session for database operations.
    """

    def __init__(self, session: Session):
        """
        Initializes the APIKeyRepository with a database session.

        Args:
            session (Session): SQLAlchemy session for database operations.
        """
        self.session = session

    def get_all(
        self, page: int = 1, page_size: int = 10, filters: dict = None
    ) -> Tuple[List[ApiKey], int]:
        """
        Retrieves all API keys with pagination and optional filters.

        Args:
            page (int): Page number for pagination. Defaults to 1.
            page_size (int): Number of items per page. Defaults to 10.
            filters (dict): Optional filters for querying API keys.

        Returns:
            Tuple[List[ApiKey], int]: A tuple containing a list of API keys and the total count.
        """
        skip = (page - 1) * page_size
        query = self.session.query(ApiKey)

        if filters:
            for attr, value in filters.items():
                query = query.filter(getattr(ApiKey, attr) == value)

        total = query.count()
        api_keys = query.offset(skip).limit(page_size).all()
        return api_keys, total

    def get(
        self, id: Optional[UUID] = None, api_key: Optional[str] = None
    ) -> Optional[ApiKey]:
        """
        Retrieve an API key by its ID or API key string.

        Args:
            id (Optional[UUID]): The unique identifier of the API key.
            api_key (Optional[str]): The API key string.

        Returns:
            Optional[ApiKey]: The ApiKey object if found, otherwise None.
        """
        query = self.session.query(ApiKey)
        if id:
            query = query.filter(ApiKey.id == id)
        if api_key:
            query = query.filter(ApiKey.api_key == api_key)
        return query.first()

    def add(self, api_key: ApiKey) -> None:
        """
        Adds a new API key to the database.

        Args:
            api_key (ApiKey): The API key to add.
        """
        self.session.add(api_key)

    def update(self, id: UUID, **kwargs: object) -> None:
        """
        Updates an existing API key with provided attributes.

        Args:
            id (UUID): The ID of the API key to update.
            **kwargs (object): Attributes to update on the API key.
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

    def delete(self, id: UUID) -> None:
        """
        Deletes an API key by its ID.

        Args:
            id (UUID): The ID of the API key to delete.
        """
        api_key = self.get(id=id)
        if api_key:
            self.session.delete(api_key)
