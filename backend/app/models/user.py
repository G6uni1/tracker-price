import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # timezone=True + datetime.now()
        nullable=False,
    )

    tracked_products = relationship(
        "TrackedProduct", back_populates="user", cascade="all, delete-orphan"
    )
    notification_settings = relationship(
        "NotificationSettings", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )