from fastapi import FastAPI
from .api.api import api_router
from .core.database import engine, Base

app = FastAPI(title="Rastreador de Preços Inteligente")

@app.on_event("startup")
async def startup():
    # Cria tabelas se não existirem (apenas dev; em produção use Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(api_router)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .scheduler.jobs import daily_scrape_job

scheduler = AsyncIOScheduler()
scheduler.add_job(daily_scrape_job, trigger='cron', hour=0, minute=0, timezone='America/Sao_Paulo')
scheduler.start()