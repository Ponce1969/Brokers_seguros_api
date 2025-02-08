from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, constr

# Importaciones para evitar referencias circulares
from .aseguradora import Aseguradora
from .movimiento_vigencia import MovimientoVigencia


class TipoSeguroBase(BaseModel):
    """Modelo base para tipos de seguro con validaciones y documentación."""
    codigo: constr(min_length=2, max_length=10) = Field(
        ..., description="Código único del tipo de seguro"
    )
    nombre: constr(min_length=2, max_length=100) = Field(
        ..., description="Nombre del tipo de seguro"
    )
    descripcion: Optional[str] = Field(
        None, description="Descripción detallada del tipo de seguro"
    )
    es_default: bool = Field(
        default=False, description="Indica si es el tipo de seguro por defecto"
    )
    esta_activo: bool = Field(
        default=True, description="Indica si el tipo de seguro está activo"
    )

    class Config:
        from_attributes = True
        str_strip_whitespace = True


class TipoSeguroCreate(TipoSeguroBase):
    """Modelo para crear un nuevo tipo de seguro."""
    pass


class TipoSeguroUpdate(TipoSeguroBase):
    """Modelo para actualizar un tipo de seguro existente."""
    codigo: Optional[constr(min_length=2, max_length=10)] = None
    nombre: Optional[constr(min_length=2, max_length=100)] = None
    descripcion: Optional[str] = None
    es_default: Optional[bool] = None
    esta_activo: Optional[bool] = None


class TipoSeguro(TipoSeguroBase):
    """Modelo completo de tipo de seguro con campos adicionales."""
    id: int
    fecha_creacion: datetime = Field(
        ..., description="Fecha de creación del registro"
    )
    fecha_actualizacion: Optional[datetime] = Field(
        None, description="Última fecha de actualización"
    )
    aseguradoras_count: Optional[int] = Field(
        0, description="Cantidad de aseguradoras que ofrecen este tipo"
    )
    movimientos_count: Optional[int] = Field(
        0, description="Cantidad de movimientos registrados"
    )


class TipoSeguroWithRelations(TipoSeguro):
    """Modelo de tipo de seguro con sus relaciones incluidas."""
    aseguradoras: List["Aseguradora"] = []
    movimientos: List["MovimientoVigencia"] = []


TipoSeguroWithRelations.model_rebuild()
