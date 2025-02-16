from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

# Importaciones para evitar referencias circulares
from .aseguradora import Aseguradora
from .movimiento_vigencia import MovimientoVigencia


class TipoSeguroBase(BaseModel):
    """Modelo base para tipos de seguro con validaciones y documentación."""

    codigo: Annotated[
        str,
        Field(
            min_length=2, max_length=10, description="Código único del tipo de seguro"
        ),
    ]
    nombre: Annotated[
        str,
        Field(min_length=2, max_length=100, description="Nombre del tipo de seguro"),
    ]
    descripcion: Optional[str] = Field(
        None, description="Descripción detallada del tipo de seguro"
    )
    es_default: bool = Field(
        default=False, description="Indica si es el tipo de seguro por defecto"
    )
    esta_activo: bool = Field(
        default=True, description="Indica si el tipo de seguro está activo"
    )
    categoria: str = Field(
        ..., description="Categoría del seguro (vida, automotor, hogar, etc.)"
    )
    cobertura: str = Field(..., description="Descripción de la cobertura")
    vigencia_default: int = Field(default=1, description="Vigencia por defecto en años")
    aseguradora_id: int = Field(
        ..., description="ID de la aseguradora que ofrece este tipo de seguro"
    )

    class Config:
        from_attributes = True
        str_strip_whitespace = True


class TipoSeguroCreate(TipoSeguroBase):
    """Modelo para crear un nuevo tipo de seguro."""

    pass


class TipoSeguroUpdate(TipoSeguroBase):
    """Modelo para actualizar un tipo de seguro existente."""

    codigo: Optional[Annotated[str, Field(min_length=2, max_length=10)]] = None
    nombre: Optional[Annotated[str, Field(min_length=2, max_length=100)]] = None
    descripcion: Optional[str] = None
    es_default: Optional[bool] = None
    esta_activo: Optional[bool] = None
    categoria: Optional[str] = None
    cobertura: Optional[str] = None
    vigencia_default: Optional[int] = None
    aseguradora_id: Optional[int] = None


class TipoSeguro(TipoSeguroBase):
    """Modelo completo de tipo de seguro con campos adicionales."""

    id: int
    fecha_creacion: datetime = Field(..., description="Fecha de creación del registro")
    fecha_actualizacion: Optional[datetime] = Field(
        None, description="Última fecha de actualización"
    )


class TipoSeguroWithRelations(TipoSeguro):
    """Modelo de tipo de seguro con sus relaciones incluidas."""

    aseguradora: Optional["Aseguradora"] = None
    movimientos: List["MovimientoVigencia"] = []


TipoSeguroWithRelations.model_rebuild()
