import pytest
from httpx import AsyncClient

from app.models.models import User


@pytest.mark.asyncio
class TestUsers:
    """Tests para endpoints de usuarios"""
    
    async def test_get_current_user(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test obtener usuario actual"""
        response = await client.get("/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "hashed_password" not in data
    
    async def test_get_current_user_without_auth(self, client: AsyncClient):
        """Test obtener usuario actual sin autenticación"""
        response = await client.get("/users/me")
        
        assert response.status_code == 401
    
    async def test_get_user_by_id(self, client: AsyncClient, test_user: User):
        """Test obtener usuario por ID"""
        response = await client.get(f"/users/{test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
    
    async def test_get_nonexistent_user(self, client: AsyncClient):
        """Test obtener usuario inexistente"""
        response = await client.get("/users/99999")
        
        assert response.status_code == 404
