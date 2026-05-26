import uuid
from sqlalchemy import Column, ForeignKey, DateTime, DECIMAL, Boolean, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("tracked_products.id", ondelete="CASCADE"), nullable=False)
    price = Column(DECIMAL(10,2))
    currency = Column(String, default="BRL")
    availability = Column(Boolean, default=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSONB)

    product = relationship("TrackedProduct", back_populates="price_history")