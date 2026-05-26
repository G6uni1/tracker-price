import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import AsyncSessionLocal
from ..models.tracked_product import TrackedProduct
from ..services.scraping_service import scrape_and_store

logger = logging.getLogger(__name__)

async def daily_scrape_job():
    logger.info("Iniciando job diário de coleta de preços")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TrackedProduct).where(TrackedProduct.is_active == True)
        )
        products = result.scalars().all()
        for product in products:
            await scrape_and_store(db, product)
            await asyncio.sleep(5)  # intervalo entre produtos para não sobrecarregar
    logger.info("Job diário finalizado")