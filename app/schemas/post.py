from pydantic import BaseModel, Field, ConfigDict
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


class PostCreate(PostBase):
    """Schema para crear post"""
    tag_ids: Optional[List[int]] = Field(
        default=[],
        description="Lista de IDs de tags a asociar"
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


class TagInPost(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class PostResponse(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInPost] = []
    
    model_config = ConfigDict(from_attributes=True)
