import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, Post, Comment


@pytest.mark.asyncio
class TestComments:
    """Tests para endpoints de comentarios"""
    
    async def test_create_comment_success(
        self, client: AsyncClient, auth_headers: dict, test_post: Post
    ):
        """Test creación exitosa de comentario"""
        response = await client.post(
            "/comments",
            json={
                "content": "Great post!",
                "post_id": test_post.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Great post!"
        assert data["post_id"] == test_post.id
        assert "author_id" in data
    
    async def test_create_comment_without_auth(self, client: AsyncClient, test_post: Post):
        """Test creación de comentario sin autenticación"""
        response = await client.post(
            "/comments",
            json={
                "content": "Comment",
                "post_id": test_post.id
            }
        )
        
        assert response.status_code == 401
    
    async def test_create_comment_nonexistent_post(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creación de comentario en post inexistente"""
        response = await client.post(
            "/comments",
            json={
                "content": "Comment",
                "post_id": 99999
            },
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_get_comments_by_post(
        self, client: AsyncClient, test_post: Post, test_comment: Comment
    ):
        """Test obtener comentarios de un post"""
        response = await client.get(f"/comments/post/{test_post.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["content"] == "Test comment"
    
    async def test_get_comments_pagination(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User, test_post: Post
    ):
        """Test paginación de comentarios"""
        # Crear múltiples comentarios
        for i in range(15):
            comment = Comment(
                content=f"Comment {i}",
                post_id=test_post.id,
                author_id=test_user.id
            )
            db_session.add(comment)
        await db_session.commit()
        
        # Primera página
        response = await client.get(f"/comments/post/{test_post.id}?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10
        
        # Segunda página
        response = await client.get(f"/comments/post/{test_post.id}?skip=10&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
    
    async def test_delete_comment_success(
        self, client: AsyncClient, auth_headers: dict, test_comment: Comment
    ):
        """Test eliminación exitosa de comentario"""
        response = await client.delete(
            f"/comments/{test_comment.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    async def test_delete_comment_without_auth(self, client: AsyncClient, test_comment: Comment):
        """Test eliminación sin autenticación"""
        response = await client.delete(f"/comments/{test_comment.id}")
        
        assert response.status_code == 401
    
    async def test_delete_comment_not_author(
        self, client: AsyncClient, test_comment: Comment, test_user2: User
    ):
        """Test eliminación por usuario que no es el autor"""
        login_response = await client.post(
            "/auth/login",
            data={"username": "testuser2", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.delete(
            f"/comments/{test_comment.id}",
            headers=headers
        )
        
        assert response.status_code == 403
    
    async def test_delete_nonexistent_comment(self, client: AsyncClient, auth_headers: dict):
        """Test eliminación de comentario inexistente"""
        response = await client.delete("/comments/99999", headers=auth_headers)
        
        assert response.status_code == 404
