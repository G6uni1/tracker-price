from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from ...core.database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...models.price_history import PriceHistory
from ...models.tracked_product import TrackedProduct
from ...schemas.price_history import PriceHistoryOut

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/{product_id}", response_model=List[PriceHistoryOut])
async def get_price_history(
    product_id: str,
    days: Optional[int] = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verifica se o produto pertence ao usuário
    product = await db.get(TrackedProduct, product_id)
    if not product or product.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id, PriceHistory.collected_at >= cutoff)
        .order_by(PriceHistory.collected_at.asc())
    )
    return result.scalars().all()