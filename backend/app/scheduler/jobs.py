from sqlalchemy.orm import selectinload

async def daily_scrape_job():
    logger.info("Iniciando job diário de coleta de preços")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TrackedProduct)
            .where(TrackedProduct.is_active == True)
            .options(
                selectinload(TrackedProduct.user),  # carrega user junto
            )
        )
        products = result.scalars().all()

        semaphore = asyncio.Semaphore(5)  # máximo 5 scrapes simultâneos

        async def scrape_with_limit(product):
            async with semaphore:
                await scrape_and_store(db, product)
                await asyncio.sleep(random.uniform(2, 5))

        await asyncio.gather(
            *[scrape_with_limit(p) for p in products],
            return_exceptions=True,
        )
    logger.info(f"Job diário finalizado. {len(products)} produtos processados.")