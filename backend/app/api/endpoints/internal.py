from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta, timezone
from ...core.database import get_db
from ...models.price_history import PriceHistory
from ...schemas.price_history import PriceHistoryOut

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/history/{product_id}", response_model=List[PriceHistoryOut])
async def get_history_internal(
    product_id: str,
    days: int = 90,
    db: AsyncSession = Depends(get_db),
):
    """Endpoint interno — use apenas na rede Docker, nunca exposto ao Nginx."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(PriceHistory)
        .where(
            PriceHistory.product_id == product_id,
            PriceHistory.collected_at >= cutoff,
        )
        .order_by(PriceHistory.collected_at.asc())
    )
    return result.scalars().all()