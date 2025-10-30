import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestValidation:
    """Tests para validaciones de Pydantic"""
    
    async def test_email_validation(self, client: AsyncClient):
        """Test validación de email"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com"
        ]
        
        for email in invalid_emails:
            response = await client.post(
                "/auth/register",
                json={
                    "email": email,
                    "username": "testuser",
                    "password": "password123"
                }
            )
            assert response.status_code == 422
    
    async def test_username_length_validation(self, client: AsyncClient):
        """Test validación de longitud de username"""
        # Muy corto (menos de 3)
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "ab",
                "password": "password123"
            }
        )
        assert response.status_code == 422
        
        # Muy largo (más de 50)
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "a" * 51,
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    async def test_password_length_validation(self, client: AsyncClient):
        """Test validación de longitud de password"""
        # Muy corto (menos de 8)
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short"
            }
        )
        assert response.status_code == 422
    
    async def test_post_title_validation(self, client: AsyncClient, auth_headers: dict):
        """Test validación de título de post"""
        # Título vacío
        response = await client.post(
            "/posts",
            json={
                "title": "",
                "content": "Content"
            },
            headers=auth_headers
        )
        assert response.status_code == 422
        
        # Título muy largo (más de 200)
        response = await client.post(
            "/posts",
            json={
                "title": "a" * 201,
                "content": "Content"
            },
            headers=auth_headers
        )
        assert response.status_code == 422
    
    async def test_comment_content_validation(
        self, client: AsyncClient, auth_headers: dict, test_post
    ):
        """Test validación de contenido de comentario"""
        # Contenido vacío
        response = await client.post(
            "/comments",
            json={
                "content": "",
                "post_id": test_post.id
            },
            headers=auth_headers
        )
        assert response.status_code == 422
