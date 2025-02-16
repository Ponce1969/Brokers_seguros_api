from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field

# Importaciones para evitar referencias circulares
from .cliente import Cliente
from .corredor import Corredor


class ClienteCorredorBase(BaseModel):
    """Modelo base para la relación cliente-corredor con validaciones y documentación."""

    cliente_id: UUID4 = Field(..., description="ID del cliente")
    corredor_numero: int = Field(..., description="Número del corredor")
    fecha_asignacion: Optional[datetime] = Field(
        None, description="Fecha de asignación del corredor al cliente"
    )

    class Config:
        from_attributes = True


class ClienteCorredorCreate(ClienteCorredorBase):
    """Modelo para crear una nueva relación cliente-corredor."""

    pass


class ClienteCorredorUpdate(ClienteCorredorBase):
    """Modelo para actualizar una relación cliente-corredor existente."""

    cliente_id: Optional[UUID4] = None
    corredor_numero: Optional[int] = None
    fecha_asignacion: Optional[datetime] = None


class ClienteCorredor(ClienteCorredorBase):
    """Modelo completo de relación cliente-corredor."""

    pass


class ClienteCorredorWithRelations(ClienteCorredor):
    """Modelo de relación cliente-corredor con sus relaciones incluidas."""

    cliente: Optional["Cliente"] = None
    corredor: Optional["Corredor"] = None


ClienteCorredorWithRelations.model_rebuild()
