from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
import re


class TagBase(BaseModel):
    """Schema base para tag"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Nombre del tag (solo letras, números, guiones y guiones bajos)"
    )
    
    @field_validator('name')
    @classmethod
    def validate_tag_name(cls, v: str) -> str:
        """Validar formato del nombre del tag"""
        v = v.strip()
        if not v:
            raise ValueError('Tag name cannot be empty or only whitespace')
        
        # Solo permitir letras, números, guiones y guiones bajos
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Tag name can only contain letters, numbers, hyphens and underscores')
        
        return v.lower()  # Normalizar a minúsculas
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "python"
            }
        }
    )


class TagCreate(TagBase):
    """Schema para crear tag"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "fastapi"
            }
        }
    )


class TagResponse(TagBase):
    """Schema para respuesta de tag"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "python",
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00"
            }
        }
    )
