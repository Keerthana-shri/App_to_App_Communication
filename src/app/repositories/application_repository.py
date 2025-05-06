from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.app.repositories.base_repository import BaseRepository
from src.app.models.data_models import Application


class ApplicationRepository(BaseRepository[Application]):
    """
    A repository class for Application model.
    It provides methods to perform CRUD operations on Application data.
    """

    def get_all(
        self,
        name: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List[Application]:
        query = self.session.query(Application)

        if name:
            query = query.filter(Application.name == name)

        query = query.offset((page - 1) * page_size).limit(page_size)

        return query.all()

    def get(self, id: UUID) -> Optional[Application]:
        return self.session.query(Application).filter(Application.id == id).first()

    def add(self, **kwargs: object) -> None:
        application = Application(**kwargs)
        self.session.add(application)

    def update(self, id: UUID, **kwargs: object) -> None:
        application = self.get(id=id)
        if application:
            for key, value in kwargs.items():
                setattr(application, key, value)

    def delete(self, id: UUID) -> None:
        application = self.get(id=id)
        if application:
            self.session.delete(application)
