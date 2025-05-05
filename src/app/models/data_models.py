from sqlalchemy import Column, String, Text, Integer, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid
import enum

Base = declarative_base()

# Enums for Permissions and Log Status
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

# User Table
class User(Base):
    """
    Represents a user entity in the database.

    Attributes:
        id (UUID): Unique identifier for the user.
        name (String): Name of the user.
        email (String): Email address of the user.
        created_at (DateTime): Timestamp when the user was created.
        updated_at (DateTime): Timestamp when the user was last updated.
        providers (relationship): Relationship to the Provider model.
        api_keys (relationship): Relationship to the APIKey model.
    """
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    providers = relationship("Provider", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")

# Application Table
class Application(Base):
    """
    Represents an application entity in the database.

    Attributes:
        id (UUID): Unique identifier for the application.
        name (String): Name of the application.
        created_at (DateTime): Timestamp when the application was created.
        updated_at (DateTime): Timestamp when the application was last updated.
        consumer_api_keys (relationship): Relationship to API keys where the application is a consumer.
        provider_api_keys (relationship): Relationship to API keys where the application is a provider.
        consumer_logs (relationship): Relationship to logs where the application is a consumer.
        provider_logs (relationship): Relationship to logs where the application is a provider.
    """
    __tablename__ = 'application'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    consumer_api_keys = relationship("APIKey", foreign_keys="[APIKey.consumer_application_id]", back_populates="consumer_application")
    provider_api_keys = relationship("APIKey", foreign_keys="[APIKey.provider_application_id]", back_populates="provider_application")
    consumer_logs = relationship("Log", foreign_keys="[Log.consumer_application_id]", back_populates="consumer_application")
    provider_logs = relationship("Log", foreign_keys="[Log.provider_application_id]", back_populates="provider_application")

# Provider Table
class Provider(Base):
    """
    Represents a provider entity in the database.

    Attributes:
        id (UUID): Unique identifier for the provider, linked to a user.
        secret_hash (Text): Hashed secret for the provider.
        name (String): Name of the provider.
        comment (Text): Optional comment about the provider.
        created_at (DateTime): Timestamp when the provider was created.
        updated_at (DateTime): Timestamp when the provider was last updated.
        user (relationship): Relationship to the User model.
    """
    __tablename__ = 'provider'

    id = Column(UUID(as_uuid=True), ForeignKey('user.id'), primary_key=True, default=uuid.uuid4)
    secret_hash = Column(Text, nullable=False)
    name = Column(String, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="providers")

# API Key Table
class APIKey(Base):
    """
    Represents an API key entity in the database.

    Attributes:
        id (UUID): Unique identifier for the API key.
        consumer_application_id (UUID): Foreign key linking to the consumer application.
        consumer_name (String): Name of the consumer using the API key.
        api_key (String): The API key string.
        provider_application_id (UUID): Foreign key linking to the provider application.
        provider_name (String): Name of the provider associated with the API key.
        permissions (Enum): Permissions associated with the API key.
        api_key_owner (UUID): Foreign key linking to the user who owns the API key.
        is_active (Boolean): Indicates if the API key is active.
        created_at (DateTime): Timestamp when the API key was created.
        expires_at (DateTime): Expiration timestamp for the API key (nullable).
        comment (Text): Optional comment about the API key.
        consumer_application (relationship): Relationship to the consumer application.
        provider_application (relationship): Relationship to the provider application.
        user (relationship): Relationship to the User model.
    """
    __tablename__ = 'api_key'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consumer_application_id = Column(UUID(as_uuid=True), ForeignKey('application.id'))
    consumer_name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    provider_application_id = Column(UUID(as_uuid=True), ForeignKey('application.id'))
    provider_name = Column(String, nullable=False)
    permissions = Column(Enum(PermissionEnum), nullable=False)
    api_key_owner = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    comment = Column(Text)

    # Relationships
    consumer_application = relationship("Application", foreign_keys=[consumer_application_id], back_populates="consumer_api_keys")
    provider_application = relationship("Application", foreign_keys=[provider_application_id], back_populates="provider_api_keys")
    user = relationship("User", back_populates="api_keys")

# Log Table
class Log(Base):
    """
    Represents a log entry in the database.

    Attributes:
        id (UUID): Unique identifier for the log entry.
        provider_application_id (UUID): Foreign key linking to the provider application.
        consumer_application_id (UUID): Foreign key linking to the consumer application.
        request_url (String): URL of the request.
        request_data (Text): Data sent in the request.
        status (Enum): Status of the log entry (e.g., Success or Failed).
        response_data (Text): Data received in the response.
        response_code (Integer): HTTP response code.
        retry_count (Integer): Number of retries for the request.
        http_method (String): HTTP method used for the request.
        created_at (DateTime): Timestamp when the log entry was created.
        updated_at (DateTime): Timestamp when the log entry was last updated.
        provider_application (relationship): Relationship to the provider application.
        consumer_application (relationship): Relationship to the consumer application.
    """
    __tablename__ = 'log'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_application_id = Column(UUID(as_uuid=True), ForeignKey('application.id'))
    consumer_application_id = Column(UUID(as_uuid=True), ForeignKey('application.id'))
    request_url = Column(String, nullable=False)
    request_data = Column(Text)
    status = Column(Enum(StatusEnum), nullable=False)
    response_data = Column(Text)
    response_code = Column(Integer)
    retry_count = Column(Integer, default=0)
    http_method = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    provider_application = relationship("Application", foreign_keys=[provider_application_id], back_populates="provider_logs")
    consumer_application = relationship("Application", foreign_keys=[consumer_application_id], back_populates="consumer_logs")