"""Dependencias reutilizables de FastAPI"""

from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import User
from app.utils.auth import decode_access_token
from app.exceptions import AuthenticationException
from app.constants import ERROR_INVALID_TOKEN, ERROR_USER_NOT_FOUND
from app.logging_config import get_logger

logger = get_logger(__name__)

# Esquema OAuth2 para autenticación con Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Obtener usuario actual desde el token JWT.
    
    Args:
        token: Token JWT del header Authorization
        db: Sesión de base de datos
    
    Returns:
        Usuario autenticado
    
    Raises:
        AuthenticationException: Si el token es inválido o el usuario no existe
    """
    # Decodificar token
    username = decode_access_token(token)
    if username is None:
        logger.warning("Invalid or expired token")
        raise AuthenticationException(detail=ERROR_INVALID_TOKEN)
    
    # Buscar usuario en base de datos
    result = await db.execute(
        select(User).where(
            User.username == username,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        logger.warning(f"User not found or deleted: {username}")
        raise AuthenticationException(detail=ERROR_USER_NOT_FOUND)
    
    return user
