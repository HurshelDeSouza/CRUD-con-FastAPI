from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import List, Optional
from app.constants import (
    MIN_POST_TITLE_LENGTH, MAX_POST_TITLE_LENGTH,
    MIN_POST_CONTENT_LENGTH
)


class PostBase(BaseModel):
    """Schema base para post"""
    title: str = Field(
        ...,
        min_length=MIN_POST_TITLE_LENGTH,
        max_length=MAX_POST_TITLE_LENGTH,
        description="Título del post"
    )
    content: str = Field(
        ...,
        min_length=MIN_POST_CONTENT_LENGTH,
        description="Contenido del post"
    )
    
    @field_validator('title', 'content')
    @classmethod
    def validate_not_empty(cls, v: str, info) -> str:
        """Validar que el campo no sea solo espacios en blanco"""
        if not v or not v.strip():
            raise ValueError(f'{info.field_name} cannot be empty or only whitespace')
        return v.strip()
    
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Eliminar espacios automáticamente
        json_schema_extra={
            "example": {
                "title": "Mi primer post en FastAPI",
                "content": "Este es el contenido de mi post sobre FastAPI..."
            }
        }
    )


class PostCreate(PostBase):
    """Schema para crear post"""
    tag_ids: Optional[List[int]] = Field(
        default=[],
        description="Lista de IDs de tags a asociar"
    )
    
    @field_validator('tag_ids')
    @classmethod
    def validate_tag_ids(cls, v: Optional[List[int]]) -> List[int]:
        """Validar que los IDs de tags sean únicos y positivos"""
        if v is None:
            return []
        if not all(tag_id > 0 for tag_id in v):
            raise ValueError('All tag IDs must be positive integers')
        # Eliminar duplicados manteniendo el orden
        return list(dict.fromkeys(v))
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Introducción a FastAPI",
                "content": "FastAPI es un framework moderno...",
                "tag_ids": [1, 2, 3]
            }
        }
    )


class PostUpdate(BaseModel):
    """Schema para actualizar post (todos los campos opcionales)"""
    title: Optional[str] = Field(
        None,
        min_length=MIN_POST_TITLE_LENGTH,
        max_length=MAX_POST_TITLE_LENGTH,
        description="Nuevo título del post"
    )
    content: Optional[str] = Field(
        None,
        min_length=MIN_POST_CONTENT_LENGTH,
        description="Nuevo contenido del post"
    )
    tag_ids: Optional[List[int]] = Field(
        None,
        description="Nueva lista de IDs de tags"
    )
    
    @field_validator('title', 'content')
    @classmethod
    def validate_not_empty(cls, v: Optional[str], info) -> Optional[str]:
        """Validar que si se proporciona, no sea solo espacios en blanco"""
        if v is not None and (not v or not v.strip()):
            raise ValueError(f'{info.field_name} cannot be empty or only whitespace')
        return v.strip() if v else None
    
    @field_validator('tag_ids')
    @classmethod
    def validate_tag_ids(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        """Validar que los IDs de tags sean únicos y positivos"""
        if v is None:
            return None
        if not all(tag_id > 0 for tag_id in v):
            raise ValueError('All tag IDs must be positive integers')
        return list(dict.fromkeys(v))
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "title": "Título actualizado",
                "content": "Contenido actualizado del post"
            }
        }
    )


class TagInPost(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class PostResponse(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInPost] = Field(default=[], description="Tags asociados al post")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Mi primer post",
                "content": "Contenido del post...",
                "author_id": 1,
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00",
                "tags": [
                    {"id": 1, "name": "Python"},
                    {"id": 2, "name": "FastAPI"}
                ]
            }
        }
    )
