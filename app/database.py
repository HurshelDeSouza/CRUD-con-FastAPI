from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Configurar engine con pool de conexiones optimizado
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Cambiar a False en producción para mejor rendimiento
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_size=5,  # Número de conexiones en el pool
    max_overflow=10  # Conexiones adicionales permitidas
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False  # Mejor control sobre cuándo hacer flush
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para obtener sesión de base de datos"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
