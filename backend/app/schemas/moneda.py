from typing import Optional, List
from pydantic import BaseModel, Field, constr

class MonedaBase(BaseModel):
    codigo: constr(min_length=2, max_length=3) = Field(..., description="Código ISO de la moneda (ej: USD, EUR, UYU)")
    descripcion: constr(min_length=3, max_length=50) = Field(..., description="Descripción completa de la moneda")
    simbolo: constr(max_length=5) = Field(..., description="Símbolo de la moneda (ej: $, €, U$S)")
    es_default: bool = Field(default=False, description="Indica si es la moneda por defecto")
    esta_activa: bool = Field(default=True, description="Indica si la moneda está activa para su uso")

class MonedaCreate(MonedaBase):
    pass

class MonedaUpdate(MonedaBase):
    codigo: Optional[constr(min_length=2, max_length=3)] = None
    descripcion: Optional[constr(min_length=3, max_length=50)] = None
    simbolo: Optional[constr(max_length=5)] = None
    es_default: Optional[bool] = None
    esta_activa: Optional[bool] = None

class Moneda(MonedaBase):
    id: int
    movimientos_count: Optional[int] = Field(0, description="Cantidad de movimientos asociados a esta moneda")

    class Config:
        from_attributes = True

class MonedaWithMovimientos(Moneda):
    movimientos: List["MovimientoVigencia"] = []

# Para evitar referencias circulares, importamos MovimientoVigencia aquí
from .movimiento_vigencia import MovimientoVigencia
MonedaWithMovimientos.model_rebuild()
