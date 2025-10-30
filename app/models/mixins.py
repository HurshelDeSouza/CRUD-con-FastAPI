from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.orm import declared_attr


class TimestampMixin:
    """Mixin para agregar timestamps automáticos a los modelos"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin para implementar soft delete en los modelos"""
    
    @declared_attr
    def is_deleted(cls):
        return Column(Boolean, default=False, nullable=False)
    
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True)
    
    def soft_delete(self):
        """Marca el registro como eliminado"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
