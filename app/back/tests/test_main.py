"""
Simple tests for the API
"""
import pytest
from fastapi.testclient import TestClient
from app.back.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_api_info():
    """Test API info endpoint"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "api_name" in data
    assert "version" in data
    assert "endpoints" in data

# Note: Database tests would require a test database setup
# def test_create_user():
#     """Test user creation"""
#     user_data = {
#         "nome": "Teste Usuario",
#         "email": "teste@email.com"
#     }
#     response = client.post("/api/v1/usuarios", json=user_data)
#     assert response.status_code == 201
