import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class AppType(enum.Enum):
    """
    Enum representing the type of application.
    - provider: Application providing services.
    - consumer: Application consuming services.
    """

    provider = "provider"
    consumer = "consumer"


class StatusEnum(enum.Enum):
    """
    Enum representing the status of an entity.
    - active: Entity is active.
    - inactive: Entity is inactive.
    - revoked: Entity access has been revoked.
    """

    active = "active"
    inactive = "inactive"
    revoked = "revoked"


class PermissionEnum(enum.Enum):
    """
    Enum representing the permissions associated with an API key.
    - read: Read-only access.
    - write: Write access.
    - both: For Read-Write both access.
    """

    read = "read"
    write = "write"
    both = "both"


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (UUID): Primary key.
        name (str): Name of the user.
        email (str): Email address of the user (unique).
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp when the user was last updated.
        applications (list): List of applications owned by the user.
        api_keys (list): List of API keys owned by the user.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    applications = relationship("Application", back_populates="owner")
    api_keys = relationship("ApiKey", back_populates="owner")


class Application(Base):
    """
    Represents an application in the system.

    Attributes:
        id (UUID): Primary key.
        name (str): Name of the application.
        secret_hash (str): Secret hash for the application.
        type (AppType): Type of the application (provider or consumer).
        status (StatusEnum): Status of the application.
        comment (str): Additional comments about the application.
        user_id (UUID): Foreign key referencing the owner (User).
        created_at (datetime): Timestamp when the application was created.
        updated_at (datetime): Timestamp when the application was last updated.
        owner (User): The user who owns the application.
        provided_keys (list): API keys provided by the application.
        consumed_keys (list): API keys consumed by the application.
        logs (list): Logs associated with the application.
    """

    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    secret_hash = Column(String(255), nullable=False)
    type = Column(Enum(AppType), nullable=False)  # provider or consumer
    status = Column(Enum(StatusEnum), default=StatusEnum.active)
    comment = Column(Text)

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="applications", passive_deletes=True)

    provided_keys = relationship(
        "ApiKey", back_populates="provider_app", foreign_keys="ApiKey.provider_id"
    )
    consumed_keys = relationship(
        "ApiKey", back_populates="consumer_app", foreign_keys="ApiKey.consumer_id"
    )

    logs = relationship(
        "Log",
        back_populates="application",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ApiKey(Base):
    """
    Represents an API key in the system.

    Attributes:
        id (UUID): Primary key.
        provider_id (UUID): Foreign key referencing the provider application.
        consumer_id (UUID): Foreign key referencing the consumer application.
        status (StatusEnum): Status of the API key.
        api_key_owner_id (UUID): Foreign key referencing the owner (User).
        permissions (PermissionEnum): Permissions associated with the API key.
        created_at (datetime): Timestamp when the API key was created.
        updated_at (datetime): Timestamp when the API key was last updated.
        expires_at (datetime): Expiration timestamp of the API key.
        comment (str): Additional comments about the API key.
        provider_app (Application): The provider application associated with the API key.
        consumer_app (Application): The consumer application associated with the API key.
        owner (User): The user who owns the API key.
    """

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(
        UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False
    )
    consumer_id = Column(
        UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False
    )
    status = Column(Enum(StatusEnum), default=StatusEnum.active)
    api_key_owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    permissions = Column(Enum(PermissionEnum), nullable=False)

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    comment = Column(Text)

    provider_app = relationship(
        "Application", foreign_keys=[provider_id], back_populates="provided_keys"
    )
    consumer_app = relationship(
        "Application", foreign_keys=[consumer_id], back_populates="consumed_keys"
    )
    owner = relationship("User", back_populates="api_keys")


class Log(Base):
    """
    Represents a log entry in the system.

    Attributes:
        id (UUID): Primary key.
        application_id (UUID): Foreign key referencing the application.
        description (str): Description of the log entry.
        created_at (datetime): Timestamp when the log entry was created.
        updated_at (datetime): Timestamp when the log entry was last updated.
        application (Application): The application associated with the log entry.
    """

    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    application = relationship("Application", back_populates="logs")
