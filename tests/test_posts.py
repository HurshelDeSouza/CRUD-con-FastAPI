import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User, Post, Tag


@pytest.mark.asyncio
class TestPosts:
    """Tests para endpoints de posts"""
    
    async def test_create_post_success(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        """Test creación exitosa de post"""
        response = await client.post(
            "/posts",
            json={
                "title": "New Post",
                "content": "This is the content of the new post",
                "tag_ids": []
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Post"
        assert data["content"] == "This is the content of the new post"
        assert "id" in data
        assert "author_id" in data
        assert "created_at" in data
    
    async def test_create_post_without_auth(self, client: AsyncClient):
        """Test creación de post sin autenticación"""
        response = await client.post(
            "/posts",
            json={
                "title": "New Post",
                "content": "Content"
            }
        )
        
        assert response.status_code == 401
    
    async def test_create_post_with_tags(
        self, client: AsyncClient, auth_headers: dict, test_tag: Tag
    ):
        """Test creación de post con tags"""
        response = await client.post(
            "/posts",
            json={
                "title": "Post with Tags",
                "content": "Content",
                "tag_ids": [test_tag.id]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["tags"]) == 1
        assert data["tags"][0]["name"] == "TestTag"
    
    async def test_get_posts_list(self, client: AsyncClient, test_post: Post):
        """Test obtener lista de posts"""
        response = await client.get("/posts")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == "Test Post"
    
    async def test_get_posts_pagination(
        self, client: AsyncClient, db_session: AsyncSession, test_user: User
    ):
        """Test paginación de posts"""
        # Crear múltiples posts
        for i in range(15):
            post = Post(
                title=f"Post {i}",
                content=f"Content {i}",
                author_id=test_user.id
            )
            db_session.add(post)
        await db_session.commit()
        
        # Primera página
        response = await client.get("/posts?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10
        
        # Segunda página
        response = await client.get("/posts?skip=10&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
    
    async def test_get_post_by_id(self, client: AsyncClient, test_post: Post):
        """Test obtener post por ID"""
        response = await client.get(f"/posts/{test_post.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_post.id
        assert data["title"] == test_post.title
    
    async def test_get_nonexistent_post(self, client: AsyncClient):
        """Test obtener post inexistente"""
        response = await client.get("/posts/99999")
        
        assert response.status_code == 404
    
    async def test_update_post_success(
        self, client: AsyncClient, auth_headers: dict, test_post: Post
    ):
        """Test actualización exitosa de post"""
        response = await client.put(
            f"/posts/{test_post.id}",
            json={
                "title": "Updated Title",
                "content": "Updated Content"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated Content"
    
    async def test_update_post_partial(
        self, client: AsyncClient, auth_headers: dict, test_post: Post
    ):
        """Test actualización parcial de post"""
        response = await client.put(
            f"/posts/{test_post.id}",
            json={"title": "Only Title Updated"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Title Updated"
        assert data["content"] == test_post.content  # No cambió
    
    async def test_update_post_without_auth(self, client: AsyncClient, test_post: Post):
        """Test actualización sin autenticación"""
        response = await client.put(
            f"/posts/{test_post.id}",
            json={"title": "Updated"}
        )
        
        assert response.status_code == 401
    
    async def test_update_post_not_author(
        self, client: AsyncClient, test_post: Post, test_user2: User
    ):
        """Test actualización por usuario que no es el autor"""
        # Login con segundo usuario
        login_response = await client.post(
            "/auth/login",
            data={"username": "testuser2", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.put(
            f"/posts/{test_post.id}",
            json={"title": "Updated"},
            headers=headers
        )
        
        assert response.status_code == 403
    
    async def test_delete_post_success(
        self, client: AsyncClient, auth_headers: dict, test_post: Post, db_session: AsyncSession
    ):
        """Test eliminación exitosa de post (soft delete)"""
        response = await client.delete(
            f"/posts/{test_post.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verificar que el post está marcado como eliminado
        result = await db_session.execute(
            select(Post).where(Post.id == test_post.id)
        )
        post = result.scalar_one_or_none()
        assert post.is_deleted is True
        assert post.deleted_at is not None
        
        # Verificar que no aparece en la lista
        list_response = await client.get("/posts")
        posts = list_response.json()
        post_ids = [p["id"] for p in posts]
        assert test_post.id not in post_ids
    
    async def test_delete_post_without_auth(self, client: AsyncClient, test_post: Post):
        """Test eliminación sin autenticación"""
        response = await client.delete(f"/posts/{test_post.id}")
        
        assert response.status_code == 401
    
    async def test_delete_post_not_author(
        self, client: AsyncClient, test_post: Post, test_user2: User
    ):
        """Test eliminación por usuario que no es el autor"""
        login_response = await client.post(
            "/auth/login",
            data={"username": "testuser2", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.delete(
            f"/posts/{test_post.id}",
            headers=headers
        )
        
        assert response.status_code == 403
    
    async def test_create_post_invalid_title(self, client: AsyncClient, auth_headers: dict):
        """Test creación con título inválido"""
        response = await client.post(
            "/posts",
            json={
                "title": "",  # Título vacío
                "content": "Content"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
