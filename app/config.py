from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno"""
    
    # Database
    database_url: str = Field(
        ...,
        description="URL de conexión a la base de datos",
        json_schema_extra={"example": "sqlite+aiosqlite:///./blog.db"}
    )
    
    # Security
    secret_key: str = Field(
        ...,
        min_length=32,
        description="Clave secreta para JWT (mínimo 32 caracteres)"
    )
    algorithm: Literal["HS256", "HS384", "HS512"] = Field(
        default="HS256",
        description="Algoritmo de encriptación para JWT"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        gt=0,
        le=10080,  # Máximo 1 semana
        description="Tiempo de expiración del token en minutos"
    )
    
    # Application
    app_name: str = Field(
        default="FastAPI Blog API",
        description="Nombre de la aplicación"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Versión de la aplicación"
    )
    debug: bool = Field(
        default=False,
        description="Modo debug (solo para desarrollo)"
    )
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validar que la clave secreta sea suficientemente segura"""
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters long')
        if v == "your-secret-key-here" or v == "changeme":
            raise ValueError('Please change the default secret key')
        return v
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validar formato de la URL de base de datos"""
        if not v:
            raise ValueError('Database URL cannot be empty')
        # Verificar que tenga un esquema válido
        valid_schemes = ['sqlite', 'sqlite+aiosqlite', 'postgresql', 'postgresql+asyncpg', 'mysql', 'mysql+aiomysql']
        if not any(v.startswith(scheme) for scheme in valid_schemes):
            raise ValueError(f'Database URL must start with one of: {", ".join(valid_schemes)}')
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,  # Validar valores por defecto
        json_schema_extra={
            "example": {
                "database_url": "sqlite+aiosqlite:///./blog.db",
                "secret_key": "your-super-secret-key-min-32-chars-long",
                "algorithm": "HS256",
                "access_token_expire_minutes": 30,
                "app_name": "FastAPI Blog API",
                "app_version": "1.0.0",
                "debug": False
            }
        }
    )


@lru_cache()
def get_settings() -> Settings:
    """Obtener instancia singleton de configuración"""
    return Settings()


# Mantener compatibilidad con código existente
settings = get_settings()
