import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User, Post, Comment, Tag
from app.utils.auth import get_password_hash


@pytest.mark.asyncio
class TestModels:
    """Tests para modelos y mixins"""
    
    async def test_user_creation(self, db_session: AsyncSession):
        """Test creación de usuario"""
        user = User(
            email="model@test.com",
            username="modeluser",
            hashed_password=get_password_hash("password"),
            full_name="Model User"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "model@test.com"
        assert user.username == "modeluser"
        assert user.is_deleted is False
    
    async def test_timestamp_mixin(self, db_session: AsyncSession):
        """Test que TimestampMixin funciona correctamente"""
        user = User(
            email="timestamp@test.com",
            username="timestampuser",
            hashed_password="hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Verificar que created_at y updated_at se establecen
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    async def test_soft_delete_mixin(self, db_session: AsyncSession, test_user: User):
        """Test que SoftDeleteMixin funciona correctamente"""
        # Verificar estado inicial
        assert test_user.is_deleted is False
        assert test_user.deleted_at is None
        
        # Aplicar soft delete
        test_user.soft_delete()
        await db_session.commit()
        await db_session.refresh(test_user)
        
        # Verificar que está marcado como eliminado
        assert test_user.is_deleted is True
        assert test_user.deleted_at is not None
        assert isinstance(test_user.deleted_at, datetime)
    
    async def test_user_post_relationship(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test relación uno a muchos User -> Post"""
        post1 = Post(title="Post 1", content="Content 1", author_id=test_user.id)
        post2 = Post(title="Post 2", content="Content 2", author_id=test_user.id)
        
        db_session.add_all([post1, post2])
        await db_session.commit()
        
        # Recargar usuario con posts
        result = await db_session.execute(
            select(User).where(User.id == test_user.id)
        )
        user = result.scalar_one()
        
        assert len(user.posts) == 2
        assert user.posts[0].author_id == test_user.id
    
    async def test_post_comment_relationship(
        self, db_session: AsyncSession, test_user: User, test_post: Post
    ):
        """Test relación uno a muchos Post -> Comment"""
        comment1 = Comment(
            content="Comment 1",
            post_id=test_post.id,
            author_id=test_user.id
        )
        comment2 = Comment(
            content="Comment 2",
            post_id=test_post.id,
            author_id=test_user.id
        )
        
        db_session.add_all([comment1, comment2])
        await db_session.commit()
        
        # Recargar post con comentarios
        result = await db_session.execute(
            select(Post).where(Post.id == test_post.id)
        )
        post = result.scalar_one()
        
        assert len(post.comments) == 2
        assert post.comments[0].post_id == test_post.id
    
    async def test_post_tag_many_to_many(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test relación muchos a muchos Post <-> Tag"""
        # Crear tags
        tag1 = Tag(name="Python")
        tag2 = Tag(name="FastAPI")
        tag3 = Tag(name="Testing")
        
        db_session.add_all([tag1, tag2, tag3])
        await db_session.commit()
        
        # Crear post con tags
        post = Post(
            title="Post with Tags",
            content="Content",
            author_id=test_user.id,
            tags=[tag1, tag2]
        )
        
        db_session.add(post)
        await db_session.commit()
        await db_session.refresh(post)
        
        # Verificar relación
        assert len(post.tags) == 2
        assert tag1 in post.tags
        assert tag2 in post.tags
        
        # Verificar relación inversa
        await db_session.refresh(tag1)
        assert post in tag1.posts
    
    async def test_cascade_delete(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test que las relaciones en cascada funcionan"""
        post = Post(
            title="Post to Delete",
            content="Content",
            author_id=test_user.id
        )
        db_session.add(post)
        await db_session.commit()
        
        comment = Comment(
            content="Comment",
            post_id=post.id,
            author_id=test_user.id
        )
        db_session.add(comment)
        await db_session.commit()
        
        # Eliminar post (físicamente para probar cascade)
        await db_session.delete(post)
        await db_session.commit()
        
        # Verificar que el comentario también se eliminó
        result = await db_session.execute(
            select(Comment).where(Comment.id == comment.id)
        )
        deleted_comment = result.scalar_one_or_none()
        assert deleted_comment is None
