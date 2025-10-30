from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import User
from app.schemas.user import UserResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# Type aliases
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
    description="Obtiene información del usuario autenticado"
)
async def get_current_user_info(current_user: CurrentUser):
    """Obtener información del usuario actual autenticado"""
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Obtiene información de un usuario específico"
)
async def get_user(user_id: int, db: DBSession):
    """Obtener usuario por ID"""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
