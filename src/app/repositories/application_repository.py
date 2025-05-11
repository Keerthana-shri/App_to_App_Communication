from typing import List, Optional
from uuid import UUID

from sqlalchemy import asc, desc

from src.app.models.data_models import Application
from src.app.repositories.base_repository import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    """
    Repository class for handling application-related database operations.
    """

    def get_all(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,
        sort_by: Optional[str] = "created_at",
        order: Optional[str] = "asc",
    ) -> List[Application]:
        """
        Retrieve all applications or filter them by name and type.
        Parameters:
            name (str, optional): Filter applications by name.
            type (str, optional): Filter applications by type.
            sort_by (str, optional): Column name to sort results.
                - Expected values: "name", "status", "created_at", "updated_at"
                - Defaults to "created_at"
            order (str, optional): Sorting order ("asc" or "desc"). Defaults to "asc".
        Returns:
            List[Application]: A list of application records.
        """
        query = self.session.query(Application)

        if name:
            query = query.filter(Application.name == name)

        if type:
            query = query.filter(Application.type == type)

        sort_column = getattr(Application, sort_by, None)
        if sort_column:
            query = query.order_by(
                asc(sort_column) if order == "asc" else desc(sort_column)
            )

        return query.all()

    def get(self, id: UUID) -> Optional[Application]:
        """
        Retrieve a single application by its unique identifier.
        Parameters:
            id (UUID): The unique identifier of the application.
        Returns:
            Application | None: The application record if found, else None.
        """
        return self.session.query(Application).filter(Application.id == id).first()

    def add(self, **kwargs: object) -> None:
        """
        Add a new application record to the database.
        Parameters:
            kwargs (object): Key-value pairs of attributes for the new application.
        """
        application = Application(**kwargs)
        self.session.add(application)

    def update(self, id: UUID, **kwargs: object) -> None:
        """
        Update an existing application record.
        Parameters:
            id (UUID): The unique identifier of the application to update.
            kwargs (object): Key-value pairs of attributes to update.
        """
        application = self.get(id=id)
        if application:
            for key, value in kwargs.items():
                setattr(application, key, value)

    def delete(self, id: UUID) -> None:
        """
        Delete an application by ID.
        Parameters:
            id (UUID): The unique identifier of the application.
        """
        application = self.get(id=id)
        if application:
            self.session.delete(application)
