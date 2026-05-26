from sqlalchemy import Column, ForeignKey, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base

class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    email_enabled = Column(Boolean, default=True)
    telegram_chat_id = Column(String)
    discord_webhook_url = Column(String)
    notify_on_drop = Column(Boolean, default=True)
    notify_on_rise = Column(Boolean, default=False)
    notify_on_restock = Column(Boolean, default=True)

    user = relationship("User", back_populates="notification_settings")