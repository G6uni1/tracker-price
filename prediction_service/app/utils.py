import httpx
from typing import List, Dict

BACKEND_INTERNAL_URL = "http://backend:8000/api/v1/internal"


async def fetch_price_history(product_id: str, days: int = 90) -> List[Dict]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BACKEND_INTERNAL_URL}/history/{product_id}",
            params={"days": days},
        )
        response.raise_for_status()
        return response.json()