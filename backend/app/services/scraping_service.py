import time
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import AsyncSessionLocal
from ..models.tracked_product import TrackedProduct
from ..models.price_history import PriceHistory
from ..models.scraper_log import ScraperLog
from ..scraper.manager import run_scraper
from ..notifications.notifier import notify_price_change

logger = logging.getLogger(__name__)


async def scrape_and_store(product: TrackedProduct) -> None:
    """Cada produto usa sua própria sessão de banco — evita race conditions."""
    async with AsyncSessionLocal() as db:  # sessão própria por produto
        start = time.time()
        try:
            data = await run_scraper(product.store, product.url)

            if data is None:
                db.add(ScraperLog(
                    product_id=product.id,
                    status="error",
                    message="Scraper retornou None",
                    execution_time_ms=int((time.time() - start) * 1000),
                ))
                await db.commit()
                return

            # Re-busca o produto nesta sessão
            db_product = await db.get(TrackedProduct, product.id)
            if not db_product:
                return

            if data.get("name") and data["name"] != db_product.product_name:
                db_product.product_name = data["name"]

            last_entry = (
                await db.execute(
                    select(PriceHistory)
                    .where(PriceHistory.product_id == product.id)
                    .order_by(PriceHistory.collected_at.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()

            previous_price = float(last_entry.price) if last_entry and last_entry.price else None
            availability_before = last_entry.availability if last_entry else None

            new_entry = PriceHistory(
                product_id=product.id,
                price=data.get("price"),
                availability=data.get("availability", True),
                raw_data=data,
            )
            db.add(new_entry)
            db.add(ScraperLog(
                product_id=product.id,
                status="success",
                execution_time_ms=int((time.time() - start) * 1000),
            ))
            await db.commit()

            await notify_price_change(
                db=db,
                product=db_product,
                old_price=previous_price,
                new_price=data.get("price"),
                old_availability=availability_before,
                new_availability=data.get("availability"),
            )

        except Exception as e:
            logger.error(f"Falha na coleta para {product.id}: {e}", exc_info=True)
            await db.rollback()
            try:
                db.add(ScraperLog(
                    product_id=product.id,
                    status="error",
                    message=str(e)[:500],
                    execution_time_ms=int((time.time() - start) * 1000),
                ))
                await db.commit()
            except Exception:
                logger.error(f"Falha ao salvar log de erro para {product.id}")