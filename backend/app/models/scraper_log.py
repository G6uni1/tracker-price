# backend/app/models/scraper_log.py — CORRIGIDO
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base


class ScraperLog(Base):
    __tablename__ = "scraper_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tracked_products.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String(20), nullable=False)  # success, error, blocked
    message = Column(Text)
    execution_time_ms = Column(Integer)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # <-- default= é obrigatório
        nullable=False,
    )

    product = relationship("TrackedProduct", back_populates="scraper_logs")