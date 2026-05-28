from fastapi import APIRouter
from .endpoints import auth, products, price_history, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(price_history.router)
api_router.include_router(health.router)