from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime
import enum

Base = declarative_base()

# Enum for permissions
class Permission(str, enum.Enum):
    """
    Enum representing the types of permissions available for API keys.
    """
    read = "Read"
    write = "Write"
    both = "Both"

class Provider(Base):
    """
    Represents a provider entity in the database.

    Attributes:
        id (UUID): Unique identifier for the provider.
        secret_hash (Text): Hashed secret for the provider.
        name (String): Name of the provider.
        comment (Text): Optional comment about the provider.
        created_at (DateTime): Timestamp when the provider was created.
        updated_at (DateTime): Timestamp when the provider was last updated.
        api_keys (relationship): Relationship to the APIKey model.
    """
    __tablename__ = "providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    secret_hash = Column(Text, nullable=False)
    name = Column(String, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    api_keys = relationship("APIKey", back_populates="provider")

class APIKey(Base):
    """
    Represents an API key entity in the database.

    Attributes:
        id (UUID): Unique identifier for the API key.
        consumer_id (UUID): Identifier for the consumer using the API key.
        consumer_name (String): Name of the consumer using the API key.
        api_key (String): The API key string.
        provider_application_id (UUID): Foreign key linking to the provider.
        provider_name (String): Name of the provider associated with the API key.
        permissions (Enum): Permissions associated with the API key.
        api_key_owner (String): Owner of the API key.
        is_active (Boolean): Indicates if the API key is active.
        created_at (DateTime): Timestamp when the API key was created.
        expires_at (DateTime): Expiration timestamp for the API key.
        comment (Text): Optional comment about the API key.
        provider (relationship): Relationship to the Provider model.
    """
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    consumer_id = Column(UUID(as_uuid=True), nullable=False)
    consumer_name = Column(String, nullable=False)
    
    api_key = Column(String, unique=True, nullable=False)
    
    provider_application_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"))
    provider_name = Column(String, nullable=False)
    
    permissions = Column(Enum(Permission), nullable=False)
    api_key_owner = Column(String, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    comment = Column(Text)

    # Relationship
    provider = relationship("Provider", back_populates="api_keys")
