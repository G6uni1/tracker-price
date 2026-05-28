import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, DECIMAL, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base


class TrackedProduct(Base):
    __tablename__ = "tracked_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    url = Column(String, nullable=False)
    store = Column(String(50), nullable=False)
    product_name = Column(String(500))
    target_price = Column(DECIMAL(10, 2))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="tracked_products")
    price_history = relationship(
        "PriceHistory", back_populates="product", cascade="all, delete-orphan"
    )
    scraper_logs = relationship(
        "ScraperLog", back_populates="product", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Busca de produtos ativos de um usuário (query do scheduler e dashboard)
        Index("idx_tracked_products_user_active", "user_id", "is_active"),
    )