import pytest


@pytest.mark.anyio
async def test_register_success(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "novo@example.com",
        "password": "senha123456",
        "full_name": "Novo Usuário",
    })
    assert response.status_code == 201
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "senha123456"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.anyio
async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "senha123456",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "senha123456",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "password": "correta123",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "errada123",
    })
    assert response.status_code == 401


@pytest.mark.anyio
async def test_access_protected_route_without_token(client):
    response = await client.get("/api/v1/products/")
    assert response.status_code == 401