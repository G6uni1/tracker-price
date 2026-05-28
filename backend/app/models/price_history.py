# backend/app/models/price_history.py
import uuid
from sqlalchemy import Column, ForeignKey, DateTime, DECIMAL, Boolean, String, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tracked_products.id", ondelete="CASCADE"),
        nullable=False,
    )
    price = Column(DECIMAL(10, 2), nullable=True)  # nullable intencional (sem preço = indisponível)
    currency = Column(String(3), default="BRL", nullable=False)
    availability = Column(Boolean, default=True, nullable=False)
    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    raw_data = Column(JSONB)

    product = relationship("TrackedProduct", back_populates="price_history")

    __table_args__ = (
        # Índice composto para a query mais comum: histórico de um produto por data
        Index("idx_price_history_product_date", "product_id", "collected_at"),
        # Índice para queries de disponibilidade
        Index("idx_price_history_availability", "product_id", "availability"),
    )