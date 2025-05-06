from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.app.models.data_models import Provider
from src.app.repositories.base_repository import BaseRepository


class ProviderRepository(BaseRepository[Provider]):
    """
    A repository class for Provider model.
    It provides methods to perform CRUD operations on Provider data.
    """

    def get_all(
        self,
        name: Optional[str] = None,
        secret_hash: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[Provider]:
        query = self.session.query(Provider)

        if name:
            query = query.filter(Provider.name == name)
        if secret_hash:
            query = query.filter(Provider.secret_hash == secret_hash)

        query = query.offset((page - 1) * page_size).limit(page_size)

        return query.all()

    def get(self, application_id: UUID) -> Provider:
        return (
            self.session.query(Provider)
            .filter_by(application_id=application_id)
            .first()
        )

    def add(self, **kwargs: object) -> None:
        provider = Provider(**kwargs)
        self.session.add(provider)

    def update(self, application_id: UUID, **kwargs: object) -> None:
        provider = self.get(application_id=application_id)
        if provider:
            for key, value in kwargs.items():
                setattr(provider, key, value)

    def delete(self, application_id: UUID) -> None:
        provider = self.get(application_id=application_id)
        if provider:
            self.session.delete(provider)
