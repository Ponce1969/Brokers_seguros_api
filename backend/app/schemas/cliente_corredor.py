from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field

# Importaciones para evitar referencias circulares
from .cliente import Cliente
from .corredor import Corredor


class ClienteCorredorBase(BaseModel):
    """Modelo base para la relación cliente-corredor con validaciones y documentación."""
    cliente_id: UUID4 = Field(
        ..., 
        description="ID del cliente"
    )
    corredor_id: int = Field(
        ..., 
        description="ID del corredor"
    )
    es_principal: bool = Field(
        default=False, 
        description="Indica si es el corredor principal del cliente"
    )
    esta_activo: bool = Field(
        default=True, 
        description="Indica si la relación está activa"
    )
    observaciones: Optional[str] = Field(
        None, 
        description="Observaciones sobre la relación"
    )

    class Config:
        from_attributes = True


class ClienteCorredorCreate(ClienteCorredorBase):
    """Modelo para crear una nueva relación cliente-corredor."""
    pass


class ClienteCorredorUpdate(ClienteCorredorBase):
    """Modelo para actualizar una relación cliente-corredor existente."""
    cliente_id: Optional[UUID4] = None
    corredor_id: Optional[int] = None
    es_principal: Optional[bool] = None
    esta_activo: Optional[bool] = None
    observaciones: Optional[str] = None


class ClienteCorredor(ClienteCorredorBase):
    """Modelo completo de relación cliente-corredor con campos adicionales."""
    id: int
    fecha_creacion: datetime = Field(
        ..., 
        description="Fecha de creación del registro"
    )
    fecha_actualizacion: Optional[datetime] = Field(
        None, 
        description="Última fecha de actualización"
    )


class ClienteCorredorWithRelations(ClienteCorredor):
    """Modelo de relación cliente-corredor con sus relaciones incluidas."""
    cliente: Optional["Cliente"] = None
    corredor: Optional["Corredor"] = None


ClienteCorredorWithRelations.model_rebuild()
