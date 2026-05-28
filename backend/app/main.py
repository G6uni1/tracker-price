from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.api import api_router
from .core.database import engine, Base
from .core.config import settings
import logging.config
from .core.logging_config import LOGGING_CONFIG
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .core.rate_limit import limiter
from .core.exceptions import unhandled_exception_handler
from starlette.middleware.base import BaseHTTPMiddleware
from .core.middleware import request_logging_middleware

app.add_middleware(BaseHTTPMiddleware, dispatch=request_logging_middleware)

app.add_exception_handler(Exception, unhandled_exception_handler)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logging.config.dictConfig(LOGGING_CONFIG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from .scheduler.jobs import daily_scrape_job# backend/app/main.py — dentro do lifespan, antes do yield
    from fastapi.middleware.cors import CORSMiddleware
    from .core.config import settings

    app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

    scheduler = AsyncIOScheduler(timezone='America/Sao_Paulo')
    scheduler.add_job(daily_scrape_job, trigger='cron', hour=0, minute=0)
    scheduler.start()

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    await engine.dispose()

app = FastAPI(title="Rastreador de Preços Inteligente", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router)