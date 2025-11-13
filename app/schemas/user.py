from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
import re
from app.constants import (
    MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
    MAX_FULL_NAME_LENGTH
)


class UserBase(BaseModel):
    """Schema base para usuario"""
    email: EmailStr = Field(..., description="Email único del usuario")
    username: str = Field(
        ...,
        min_length=MIN_USERNAME_LENGTH,
        max_length=MAX_USERNAME_LENGTH,
        description="Nombre de usuario único (alfanumérico, puede incluir _ y -)"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=MAX_FULL_NAME_LENGTH,
        description="Nombre completo del usuario"
    )
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validar que el username sea alfanumérico"""
        v = v.strip()
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (can include _ and -)')
        # No permitir que empiece o termine con guiones
        if v.startswith(('-', '_')) or v.endswith(('-', '_')):
            raise ValueError('Username cannot start or end with - or _')
        return v.lower()
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validar y limpiar el nombre completo"""
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        # Eliminar espacios múltiples
        v = re.sub(r'\s+', ' ', v)
        return v
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe"
            }
        }
    )


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        description="Contraseña del usuario (mínimo 8 caracteres)"
    )
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validar fortaleza de la contraseña"""
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Password must be at least {MIN_PASSWORD_LENGTH} characters long')
        
        # Verificar que tenga al menos una letra y un número
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepass123",
                "full_name": "New User"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema para login de usuario"""
    username: str = Field(..., description="Nombre de usuario")
    password: str = Field(..., description="Contraseña")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "password": "secretpassword123"
            }
        }
    )


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00"
            }
        }
    )


class Token(BaseModel):
    """Schema para token JWT"""
    access_token: str = Field(..., description="Token de acceso JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenData(BaseModel):
    """Schema para datos decodificados del token"""
    username: Optional[str] = Field(None, description="Username extraído del token")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe"
            }
        }
    )
