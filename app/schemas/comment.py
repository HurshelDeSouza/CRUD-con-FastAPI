from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime


class CommentBase(BaseModel):
    """Schema base para comentario"""
    content: str = Field(
        ..., 
        min_length=1,
        max_length=1000,
        description="Contenido del comentario"
    )
    
    @field_validator('content')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validar que el contenido no sea solo espacios en blanco"""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or only whitespace')
        return v.strip()
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "content": "¡Excelente post! Me fue muy útil."
            }
        }
    )


class CommentCreate(CommentBase):
    """Schema para crear comentario"""
    post_id: int = Field(..., gt=0, description="ID del post al que pertenece el comentario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "Gran explicación, gracias por compartir",
                "post_id": 1
            }
        }
    )


class CommentResponse(CommentBase):
    """Schema para respuesta de comentario"""
    id: int
    post_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "content": "Muy buen post",
                "post_id": 1,
                "author_id": 2,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )
