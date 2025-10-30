import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User


@pytest.mark.asyncio
class TestAuth:
    """Tests para endpoints de autenticación"""
    
    async def test_register_user_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test registro exitoso de usuario"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "hashed_password" not in data
        
        # Verificar que el usuario existe en la base de datos
        result = await db_session.execute(
            select(User).where(User.username == "newuser")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == "newuser@example.com"
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registro con email duplicado"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",  # Email ya existe
                "username": "differentuser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_register_duplicate_username(self, client: AsyncClient, test_user: User):
        """Test registro con username duplicado"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "different@example.com",
                "username": "testuser",  # Username ya existe
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registro con email inválido"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "username": "testuser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_register_short_password(self, client: AsyncClient):
        """Test registro con contraseña muy corta"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short"  # Menos de 8 caracteres
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_short_username(self, client: AsyncClient):
        """Test registro con username muy corto"""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "ab",  # Menos de 3 caracteres
                "password": "password123"
            }
        )
        
        assert response.status_code == 422
    
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test login exitoso"""
        response = await client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Test login con contraseña incorrecta"""
        response = await client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login con usuario inexistente"""
        response = await client.post(
            "/auth/login",
            data={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
    
    async def test_access_protected_endpoint_without_token(self, client: AsyncClient):
        """Test acceso a endpoint protegido sin token"""
        response = await client.get("/users/me")
        
        assert response.status_code == 401
    
    async def test_access_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Test acceso a endpoint protegido con token inválido"""
        response = await client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    async def test_access_protected_endpoint_with_valid_token(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test acceso a endpoint protegido con token válido"""
        response = await client.get("/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
