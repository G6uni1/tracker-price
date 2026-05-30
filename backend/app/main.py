import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from .api.api import api_router
from .core.config import settings
from .core.database import engine
from .core.exceptions import unhandled_exception_handler
from .core.logging_config import LOGGING_CONFIG
from .core.middleware import request_logging_middleware
from .core.rate_limit import limiter

# 1. Configura logging PRIMEIRO, antes de qualquer outra coisa
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # --- STARTUP ---
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from .scheduler.jobs import daily_scrape_job

    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(daily_scrape_job, trigger="cron", hour=0, minute=0)
    scheduler.start()
    logger.info("Scheduler iniciado")

    yield

    # --- SHUTDOWN ---
    scheduler.shutdown(wait=False)
    await engine.dispose()
    logger.info("App encerrado com sucesso")


# 2. Cria o app com lifespan
app = FastAPI(
    title="Rastreador de Preços Inteligente",
    version="1.0.0",
    lifespan=lifespan,
)

# 3. Registra o limiter no estado do app
app.state.limiter = limiter

# 4. Adiciona middlewares (ordem importa: último adicionado = primeiro executado)
app.add_middleware(BaseHTTPMiddleware, dispatch=request_logging_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# 5. Registra handlers de exceção
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# 6. Registra rotas
app.include_router(api_router)