import time
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.tracked_product import TrackedProduct
from ..models.price_history import PriceHistory
from ..models.scraper_log import ScraperLog
from ..scraper.manager import run_scraper
from ..notifications.notifier import notify_price_change

logger = logging.getLogger(__name__)

async def scrape_and_store(db: AsyncSession, product: TrackedProduct):
    start = time.time()
    try:
        data = await run_scraper(product.store, product.url)
        if data is None:
            log = ScraperLog(product_id=product.id, status="error", message="Scraper retornou None")
            db.add(log)
            return

        # Atualiza nome do produto se necessário
        if data.get("name") and data["name"] != product.product_name:
            product.product_name = data["name"]

        # Obtém último preço registrado
        last_price_entry = (
            await db.execute(
                select(PriceHistory)
                .where(PriceHistory.product_id == product.id)
                .order_by(PriceHistory.collected_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()

        previous_price = last_price_entry.price if last_price_entry else None
        availability_before = last_price_entry.availability if last_price_entry else None

        new_entry = PriceHistory(
            product_id=product.id,
            price=data.get("price"),
            availability=data.get("availability", True),
            raw_data=data
        )
        db.add(new_entry)
        db.add(ScraperLog(product_id=product.id, status="success",
                          execution_time_ms=int((time.time() - start) * 1000)))

        # Compara preços e dispara notificações
        await notify_price_change(
            db=db,
            product=product,
            old_price=previous_price,
            new_price=data.get("price"),
            old_availability=availability_before,
            new_availability=data.get("availability"),
            price_drop=True,  # simplificação; você ajustará conforme a lógica real
        )

    except Exception as e:
        logger.error(f"Falha na coleta para {product.id}: {e}")
        db.add(ScraperLog(product_id=product.id, status="error", message=str(e)))

    finally:
        await db.commit()