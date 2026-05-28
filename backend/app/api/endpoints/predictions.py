import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException
from ...api.deps import get_current_user
from ...models.user import User

router = APIRouter(prefix="/predictions", tags=["predictions"])
logger = logging.getLogger(__name__)

PREDICTION_SERVICE_URL = "http://prediction:8001"  # nome do container Docker


@router.get("/{product_id}")
async def get_prediction(
    product_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{PREDICTION_SERVICE_URL}/predict/{product_id}"
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Serviço de previsão indisponível")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Erro ao buscar previsão para {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")