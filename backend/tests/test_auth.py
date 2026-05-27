import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.anyio
async def test_register():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "secret123",
            "full_name": "Test User"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data