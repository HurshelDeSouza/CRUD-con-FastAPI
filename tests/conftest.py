import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base, get_db
from app.models.models import User, Post, Comment, Tag
from app.utils.auth import get_password_hash

# Base de datos de prueba en memoria
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Crear event loop para toda la sesión de pruebas"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Crear base de datos de prueba para cada test"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP de prueba"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Crear usuario de prueba"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user2(db_session: AsyncSession) -> User:
    """Crear segundo usuario de prueba"""
    user = User(
        email="test2@example.com",
        username="testuser2",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User 2"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_token(client: AsyncClient, test_user: User) -> str:
    """Obtener token de autenticación"""
    response = await client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture
async def auth_headers(auth_token: str) -> dict:
    """Headers con autenticación"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def test_post(db_session: AsyncSession, test_user: User) -> Post:
    """Crear post de prueba"""
    post = Post(
        title="Test Post",
        content="This is a test post content",
        author_id=test_user.id
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post


@pytest.fixture
async def test_tag(db_session: AsyncSession) -> Tag:
    """Crear tag de prueba"""
    tag = Tag(name="TestTag")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)
    return tag


@pytest.fixture
async def test_comment(db_session: AsyncSession, test_user: User, test_post: Post) -> Comment:
    """Crear comentario de prueba"""
    comment = Comment(
        content="Test comment",
        post_id=test_post.id,
        author_id=test_user.id
    )
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)
    return comment
