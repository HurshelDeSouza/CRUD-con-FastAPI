"""
Script para inicializar la base de datos con datos de ejemplo
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.models.models import User, Post, Comment, Tag
from app.utils.auth import get_password_hash


async def init_db():
    async with async_session_maker() as session:
        # Crear usuarios de ejemplo
        user1 = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User"
        )
        user2 = User(
            email="user@example.com",
            username="user",
            hashed_password=get_password_hash("user123"),
            full_name="Regular User"
        )
        
        session.add_all([user1, user2])
        await session.commit()
        
        # Crear tags
        tag1 = Tag(name="Python")
        tag2 = Tag(name="FastAPI")
        tag3 = Tag(name="Tutorial")
        
        session.add_all([tag1, tag2, tag3])
        await session.commit()
        
        # Crear posts
        post1 = Post(
            title="Introducción a FastAPI",
            content="FastAPI es un framework moderno y rápido para construir APIs con Python...",
            author_id=user1.id,
            tags=[tag1, tag2, tag3]
        )
        post2 = Post(
            title="SQLAlchemy Async",
            content="SQLAlchemy 2.0 introduce soporte completo para operaciones asíncronas...",
            author_id=user1.id,
            tags=[tag1]
        )
        
        session.add_all([post1, post2])
        await session.commit()
        
        # Crear comentarios
        comment1 = Comment(
            content="¡Excelente tutorial!",
            post_id=post1.id,
            author_id=user2.id
        )
        comment2 = Comment(
            content="Muy útil, gracias por compartir",
            post_id=post1.id,
            author_id=user2.id
        )
        
        session.add_all([comment1, comment2])
        await session.commit()
        
        print("✅ Base de datos inicializada con datos de ejemplo")
        print("\nUsuarios creados:")
        print("  - admin / admin123")
        print("  - user / user123")


if __name__ == "__main__":
    asyncio.run(init_db())
