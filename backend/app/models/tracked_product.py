import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class TrackedProduct(Base):
    __tablename__ = "tracked_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    store = Column(String, nullable=False)  # ex: 'amazon', 'mercadolivre'
    product_name = Column(String)
    target_price = Column(DECIMAL(10,2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tracked_products")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    scraper_logs = relationship("ScraperLog", back_populates="product", cascade="all, delete-orphan")