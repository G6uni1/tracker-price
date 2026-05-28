import pytest


@pytest.mark.anyio
async def test_add_product(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post("/api/v1/products/", json={
        "url": "https://www.mercadolivre.com.br/exemplo",
        "store": "mercadolivre",
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["store"] == "mercadolivre"
    assert "id" in data
""

@pytest.mark.anyio
async def test_list_products_empty(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.get("/api/v1/products/", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_user_cannot_access_other_users_product(client, auth_token):
    """Testa isolamento entre usuários — crítico para segurança."""
    # Usuário 1 cria produto
    headers_1 = {"Authorization": f"Bearer {auth_token}"}
    create = await client.post("/api/v1/products/", json={
        "url": "https://exemplo.com",
        "store": "amazon",
    }, headers=headers_1)
    product_id = create.json()["id"]

    # Usuário 2 tenta acessar produto do usuário 1
    reg2 = await client.post("/api/v1/auth/register", json={
        "email": "outro@example.com",
        "password": "senha123456",
    })
    token2 = reg2.json()["access_token"]
    headers_2 = {"Authorization": f"Bearer {token2}"}

    response = await client.get(f"/api/v1/products/{product_id}", headers=headers_2)
    assert response.status_code == 404  # não 403, para não revelar existência