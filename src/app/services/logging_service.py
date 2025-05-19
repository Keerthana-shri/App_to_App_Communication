from datetime import datetime
from typing import Optional
from uuid import UUID

from src.app.models.data_models import Log
from src.app.services.unit_of_work import UnitOfWork


def log_activity(
    unit_of_work: UnitOfWork, description: str, application_id: Optional[UUID] = None
):
    """
    Logs an activity for a specific application.

    Args:
        unit_of_work (UnitOfWork): The unit of work instance for database operations.
        application_id (UUID): The ID of the application associated with the activity.
        description (str): A description of the activity being logged.
    """
    with unit_of_work as uow:
        log_entry = Log(
            application_id=application_id,
            description=description,
            created_at=datetime.now(),
        )
        uow.session.add(log_entry)
