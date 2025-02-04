from typing import Optional
from pydantic import BaseModel, UUID4
from datetime import date

class MovimientoVigenciaBase(BaseModel):
    cliente_id: UUID4
    corredor_id: Optional[int] = None
    tipo_seguro_id: int
    carpeta: Optional[str] = None
    numero_poliza: str
    endoso: Optional[str] = None
    fecha_inicio: date
    fecha_vencimiento: date
    fecha_emision: Optional[date] = None
    estado_poliza: str = "activa"
    forma_pago: Optional[str] = None
    tipo_endoso: Optional[str] = None
    moneda_id: Optional[int] = None
    suma_asegurada: float
    prima: float
    comision: Optional[float] = None
    cuotas: Optional[int] = None
    observaciones: Optional[str] = None

class MovimientoVigenciaCreate(MovimientoVigenciaBase):
    pass

class MovimientoVigenciaUpdate(MovimientoVigenciaBase):
    pass

class MovimientoVigencia(MovimientoVigenciaBase):
    id: int

    class Config:
        from_attributes = True
