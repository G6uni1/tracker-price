import asyncio
import logging
import random

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..core.database import AsyncSessionLocal
from ..models.tracked_product import TrackedProduct
from ..services.scraping_service import scrape_and_store

logger = logging.getLogger(__name__)


async def daily_scrape_job() -> None:
    """Job diário: coleta preços de todos os produtos ativos."""
    logger.info("Iniciando job diário de scraping")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TrackedProduct)
            .where(TrackedProduct.is_active == True)
            .options(selectinload(TrackedProduct.user))
        )
        products = result.scalars().all()

    if not products:
        logger.info("Nenhum produto ativo para scraping")
        return

    logger.info(f"Processando {len(products)} produtos")
    semaphore = asyncio.Semaphore(5)

    async def scrape_with_limit(product: TrackedProduct) -> None:
        async with semaphore:
            try:
                await scrape_and_store(product)
            except Exception as e:
                logger.error(f"Erro inesperado para produto {product.id}: {e}", exc_info=True)
            await asyncio.sleep(random.uniform(2, 5))

    results = await asyncio.gather(
        *[scrape_with_limit(p) for p in products],
        return_exceptions=True,
    )

    errors = sum(1 for r in results if isinstance(r, Exception))
    logger.info(f"Job finalizado. {len(products) - errors} OK, {errors} erros.")