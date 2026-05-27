# conftest.py
import pytest
import requests

API_URL = "http://localhost:8000"

def login():
    """Função auxiliar para obter um novo token"""
    response = requests.post(f"{API_URL}/login", json={
        "username": "usuario",
        "password": "senha"
    })
    response.raise_for_status()
    return response.json()["access_token"]

@pytest.fixture
def token():
    """Fixture que garante um token válido"""
    token_value = login()

    def _get_token():
        # Testa se o token ainda é válido
        check = requests.get(f"{API_URL}/me", headers={
            "Authorization": f"Bearer {token_value}"
        })
        if check.status_code == 401:  # expirou
            return login()
        return token_value

    return _get_token
