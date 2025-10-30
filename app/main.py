from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.timing import TimingMiddleware
from app.routers import auth, users, posts, comments
from app.database import engine
from app.models.models import Base
from app.logging_config import setup_logging, get_logger

# Configurar logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    logger.info("Starting FastAPI Blog API...")
    
    # Startup: Crear tablas si no existen (solo para desarrollo)
    # En producción usar Alembic
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown: Cerrar conexiones
    logger.info("Shutting down FastAPI Blog API...")
    await engine.dispose()


app = FastAPI(
    title="FastAPI Blog API",
    description="RESTful API con FastAPI, SQLAlchemy y Pydantic v2",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS (ajustar según necesidades)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middleware personalizado
app.add_middleware(TimingMiddleware)

# Incluir routers con prefijo API
API_V1_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(users.router, prefix=API_V1_PREFIX)
app.include_router(posts.router, prefix=API_V1_PREFIX)
app.include_router(comments.router, prefix=API_V1_PREFIX)


@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Welcome to FastAPI Blog API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint para monitoreo"""
    return {"status": "healthy", "service": "fastapi-blog-api"}
