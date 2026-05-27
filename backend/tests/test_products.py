import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.anyio
async def test_add_product(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with AsyncClient(app=app, base_url="http://test", headers=headers) as client:
        response = await client.post("/api/v1/products/", json={
            "url": "https://www.mercadolivre.com.br/exemplo",
            "store": "mercadolivre"
        })
        assert response.status_code == 201
        assert response.json()["store"] == "mercadolivre"