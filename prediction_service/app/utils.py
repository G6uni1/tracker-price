import httpx
from typing import List, Dict

API_BASE_URL = "http://backend:8000/api/v1"

async def fetch_price_history(product_id: str, days: int = 90) -> List[Dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/history/{product_id}?days={days}")
        response.raise_for_status()
        return response.json()