from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


def to_lower(s: str) -> str:
    """Convierte una cadena a minúsculas."""
    return s.lower()


class MonedaBase(BaseModel):
    """Modelo base para monedas con validaciones y documentación."""
    
    codigo: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Código único de la moneda (ej: USD, EUR)"
    )
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nombre de la moneda"
    )
    simbolo: str = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Símbolo de la moneda"
    )
    descripcion: Optional[str] = Field(
        None,
        description="Descripción adicional de la moneda"
    )
    es_default: bool = Field(
        default=False,
        description="Indica si es la moneda por defecto"
    )
    esta_activa: bool = Field(
        default=True,
        description="Indica si la moneda está activa"
    )

    @field_validator('codigo', 'nombre', 'simbolo')
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        from_attributes = True


class MonedaCreate(MonedaBase):
    """Modelo para crear una nueva moneda."""
    pass


class MonedaUpdate(MonedaBase):
    """Modelo para actualizar una moneda existente."""
    
    codigo: Optional[str] = Field(None, min_length=2, max_length=10)
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    simbolo: Optional[str] = Field(None, min_length=1, max_length=5)
    descripcion: Optional[str] = None
    es_default: Optional[bool] = None
    esta_activa: Optional[bool] = None


class Moneda(MonedaBase):
    """Modelo completo de moneda con campos adicionales."""
    
    id: int
    fecha_creacion: datetime = Field(
        ...,
        description="Fecha de creación del registro"
    )
    fecha_actualizacion: Optional[datetime] = Field(
        None,
        description="Última fecha de actualización"
    )
    movimientos_count: Optional[int] = Field(
        0,
        description="Cantidad de movimientos en esta moneda"
    )

    class Config:
        from_attributes = True
        alias_generator = to_lower


class MonedaWithMovimientos(Moneda):
    """Modelo de moneda con sus movimientos incluidos."""
    
    movimientos: List["MovimientoVigencia"] = Field(default_factory=list)


# Las referencias a otros modelos se definen como strings para evitar importaciones circulares
MovimientoVigencia = "MovimientoVigencia"
