@router.get("/{product_id}/stats")
async def get_price_stats(product_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = await db.get(TrackedProduct, product_id)
    if not product or product.user_id != current_user.id:
        raise HTTPException(status_code=404)

    stats_query = await db.execute(
        select(
            func.min(PriceHistory.price).label("min"),
            func.max(PriceHistory.price).label("max"),
            func.avg(PriceHistory.price).label("avg"),
            func.count(PriceHistory.id).label("count")
        ).where(PriceHistory.product_id == product_id, PriceHistory.price.isnot(None))
    )
    row = stats_query.one()
    first_price = await db.execute(
        select(PriceHistory.price).where(PriceHistory.product_id == product_id, PriceHistory.price.isnot(None))
        .order_by(PriceHistory.collected_at.asc()).limit(1)
    )
    first_price = first_price.scalar()
    last_price = await db.execute(...) # similar com desc
    # Calcula variação percentual
    variation = ((last_price - first_price) / first_price * 100) if first_price and last_price else 0
    return {
        "min": row.min,
        "max": row.max,
        "avg": float(row.avg),
        "count": row.count,
        "first_price": first_price,
        "last_price": last_price,
        "variation_percent": round(variation, 2)
    }