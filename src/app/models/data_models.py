import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class PermissionEnum(enum.Enum):
    """
    Enum representing the types of permissions available for API keys.
    """

    Read = "Read"
    Write = "Write"
    Both = "Both"


class StatusEnum(enum.Enum):
    """
    Enum representing the status of a log entry.
    """

    Success = "Success"
    Failed = "Failed"


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (UUID): Unique identifier for the user.
        name (str): Name of the user.
        email (str): Email address of the user.
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp when the user was last updated.
        api_keys (list): List of API keys owned by the user.
    """

    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )


class Application(Base):
    """
    Represents an application in the system.

    Attributes:
        id (UUID): Unique identifier for the application.
        name (str): Name of the application.
        created_at (datetime): Timestamp when the application was created.
        updated_at (datetime): Timestamp when the application was last updated.
    """

    __tablename__ = "application"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )


class Provider(Base):
    """
    Represents a provider in the system.

    Attributes:
        id (UUID): Unique identifier for the provider.
        secret_hash (str): Secret hash for the provider.
        name (str): Name of the provider.
        comment (str): Additional comments about the provider.
        application_id (UUID): Foreign key to the associated application.
        created_at (datetime): Timestamp when the provider was created.
        updated_at (datetime): Timestamp when the provider was last updated.
    """

    __tablename__ = "provider"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    secret_hash = Column(Text, nullable=False)
    name = Column(String, nullable=False)
    comment = Column(Text)
    application_id = Column(
        UUID(as_uuid=True), ForeignKey("application.id"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )


class APIKey(Base):
    """
    Represents an API key in the system.

    Attributes:
        id (UUID): Unique identifier for the API key.
        consumer_application_id (UUID): Foreign key to the consumer application.
        consumer_name (str): Name of the consumer.
        api_key (str): The API key value.
        provider_application_id (UUID): Foreign key to the provider application.
        provider_name (str): Name of the provider.
        permissions (PermissionEnum): Permissions associated with the API key.
        api_key_owner (UUID): Foreign key to the owner of the API key.
        is_active (bool): Whether the API key is active.
        created_at (datetime): Timestamp when the API key was created.
        expires_at (datetime): Expiration timestamp for the API key.
        comment (str): Additional comments about the API key.
    """

    __tablename__ = "api_key"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consumer_application_id = Column(UUID(as_uuid=True), ForeignKey("application.id"))
    consumer_name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    provider_application_id = Column(UUID(as_uuid=True), ForeignKey("application.id"))
    provider_name = Column(String, nullable=False)
    permissions = Column(Enum(PermissionEnum), nullable=False)
    api_key_owner = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    comment = Column(Text)


class Log(Base):
    """
    Represents a log entry in the system.

    Attributes:
        id (UUID): Unique identifier for the log entry.
        provider_application_id (UUID): Foreign key to the provider application.
        consumer_application_id (UUID): Foreign key to the consumer application.
        request_url (str): URL of the request.
        request_data (str): Data sent in the request.
        status (StatusEnum): Status of the log entry.
        response_data (str): Data received in the response.
        response_code (int): HTTP response code.
        retry_count (int): Number of retries for the request.
        http_method (str): HTTP method used for the request.
        created_at (datetime): Timestamp when the log entry was created.
        updated_at (datetime): Timestamp when the log entry was last updated.
    """

    __tablename__ = "log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_application_id = Column(UUID(as_uuid=True), ForeignKey("provider.id"))
    consumer_application_id = Column(UUID(as_uuid=True), ForeignKey("provider.id"))
    request_url = Column(String, nullable=False)
    request_data = Column(Text)
    status = Column(Enum(StatusEnum), nullable=False)
    response_data = Column(Text)
    response_code = Column(Integer)
    retry_count = Column(Integer, default=0)
    http_method = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
