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


# ... [imports remain unchanged]

Base = declarative_base()

# Enums remain unchanged...


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # Relationships
    api_keys = relationship(
        "APIKey", back_populates="owner", cascade="all, delete-orphan"
    )


class Application(Base):
    __tablename__ = "application"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # Relationships
    consumer_api_keys = relationship(
        "APIKey",
        foreign_keys="[APIKey.consumer_application_id]",
        back_populates="consumer_application",
    )
    provider_api_keys = relationship(
        "APIKey",
        foreign_keys="[APIKey.provider_application_id]",
        back_populates="provider_application",
    )
    consumer_logs = relationship(
        "Log",
        foreign_keys="[Log.consumer_application_id]",
        back_populates="consumer_application",
    )
    provider_logs = relationship(
        "Log",
        foreign_keys="[Log.provider_application_id]",
        back_populates="provider_application",
    )
    provider = relationship("Provider", back_populates="application", uselist=False)


class Provider(Base):
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

    # Relationships

    application = relationship("Application", back_populates="provider", uselist=False)
    consumer_api_keys = relationship(
        "APIKey",
        foreign_keys="[APIKey.consumer_application_id]",
        back_populates="consumer_provider",
    )
    provider_api_keys = relationship(
        "APIKey",
        foreign_keys="[APIKey.provider_application_id]",
        back_populates="provider_provider",
    )
    consumer_logs = relationship(
        "Log",
        foreign_keys="[Log.consumer_application_id]",
        back_populates="consumer_provider",
    )
    provider_logs = relationship(
        "Log",
        foreign_keys="[Log.provider_application_id]",
        back_populates="provider_provider",
    )


class APIKey(Base):
    __tablename__ = "api_key"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consumer_application_id = Column(UUID(as_uuid=True), ForeignKey("provider.id"))
    consumer_name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    provider_application_id = Column(UUID(as_uuid=True), ForeignKey("provider.id"))
    provider_name = Column(String, nullable=False)
    permissions = Column(Enum(PermissionEnum), nullable=False)
    api_key_owner = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    comment = Column(Text)

    # Relationships
    consumer_application = relationship(
        "Provider",
        foreign_keys=[consumer_application_id],
        back_populates="consumer_api_keys",
    )
    provider_application = relationship(
        "Provider",
        foreign_keys=[provider_application_id],
        back_populates="provider_api_keys",
    )
    owner = relationship(
        "User", foreign_keys=[api_key_owner], back_populates="api_keys"
    )
    consumer_provider = relationship(
        "Provider",
        foreign_keys=[consumer_application_id],
        back_populates="consumer_api_keys",
    )
    provider_provider = relationship(
        "Provider",
        foreign_keys=[provider_application_id],
        back_populates="provider_api_keys",
    )


class Log(Base):
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

    # Relationships
    provider_application = relationship(
        "Application",
        foreign_keys=[provider_application_id],
        back_populates="provider_logs",
    )
    consumer_application = relationship(
        "Application",
        foreign_keys=[consumer_application_id],
        back_populates="consumer_logs",
    )
