from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.utils.auth import verify_password, get_password_hash, create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Type aliases para mejor legibilidad
DBSession = Annotated[AsyncSession, Depends(get_db)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario con email y username únicos"
)
async def register(user_data: UserCreate, db: DBSession):
    """
    Registrar un nuevo usuario en el sistema.
    
    - **email**: Email único del usuario
    - **username**: Nombre de usuario único (3-50 caracteres)
    - **password**: Contraseña (mínimo 8 caracteres)
    - **full_name**: Nombre completo (opcional)
    """
    # Verificar si el usuario ya existe
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Autenticar usuario y obtener token JWT"
)
async def login(form_data: OAuth2Form, db: DBSession):
    """
    Iniciar sesión con username y password.
    
    Retorna un token JWT que debe incluirse en el header Authorization
    como "Bearer {token}" para acceder a endpoints protegidos.
    """
    # Buscar usuario activo
    result = await db.execute(
        select(User).where(
            User.username == form_data.username,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()
    
    # Verificar credenciales
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
