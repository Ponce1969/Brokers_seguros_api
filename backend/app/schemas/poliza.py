from datetime import date
from enum import Enum
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TipoDuracion(str, Enum):
    """Enumeración para los tipos de duración de pólizas."""
    diaria = "diaria"
    semanal = "semanal"
    mensual = "mensual"
    trimestral = "trimestral"
    semestral = "semestral"
    anual = "anual"


class PolizaBase(BaseModel):
    """Esquema base para pólizas (MovimientoVigencia)."""
    cliente_id: UUID
    corredor_id: Optional[int] = None
    tipo_seguro_id: int
    carpeta: Optional[str] = None
    numero_poliza: str = Field(..., description="Número único de póliza")
    endoso: Optional[str] = None
    fecha_inicio: date
    fecha_vencimiento: date
    fecha_emision: Optional[date] = None
    estado_poliza: str = Field(default="activa", description="Estado de la póliza: activa, vencida, cancelada, etc.")
    forma_pago: Optional[str] = None
    tipo_endoso: Optional[str] = None
    moneda_id: Optional[int] = None
    suma_asegurada: float = Field(..., gt=0, description="Monto asegurado")
    prima: float = Field(..., gt=0, description="Prima del seguro")
    comision: Optional[float] = None
    cuotas: Optional[int] = Field(None, ge=1, description="Número de cuotas")
    observaciones: Optional[str] = None
    tipo_duracion: TipoDuracion = Field(
        default=TipoDuracion.anual,
        description="Tipo de duración de la póliza"
    )


class PolizaCreate(PolizaBase):
    """Esquema para crear una nueva póliza."""
    @field_validator('fecha_vencimiento')
    def fecha_vencimiento_valida(cls, v: date, info) -> date:
        if 'fecha_inicio' in info.data and 'tipo_duracion' in info.data:
            inicio = info.data['fecha_inicio']
            tipo_duracion = info.data['tipo_duracion']
            
            # Para pólizas diarias, la fecha de vencimiento puede ser igual a la fecha de inicio
            if tipo_duracion == TipoDuracion.diaria:
                if v < inicio:
                    raise ValueError('La fecha de vencimiento no puede ser anterior a la fecha de inicio')
            else:
                if v <= inicio:
                    raise ValueError('La fecha de vencimiento debe ser posterior a la fecha de inicio')
        return v

    @field_validator('comision')
    def comision_valida(cls, v: Optional[float], info) -> Optional[float]:
        if v is not None:
            if v < 0:
                raise ValueError('La comisión no puede ser negativa')
            if 'prima' in info.data and v > info.data['prima']:
                raise ValueError('La comisión no puede ser mayor que la prima')
        return v

    @field_validator('tipo_duracion')
    def validar_duracion_fechas(cls, v: TipoDuracion, info) -> TipoDuracion:
        if 'fecha_inicio' in info.data and 'fecha_vencimiento' in info.data:
            inicio = info.data['fecha_inicio']
            vencimiento = info.data['fecha_vencimiento']
            dias = (vencimiento - inicio).days + 1  # +1 para incluir el día de inicio
            
            # Validar que la duración coincida con el tipo seleccionado
            if v == TipoDuracion.diaria and dias > 1:
                raise ValueError('Una póliza diaria no puede durar más de 1 día')
            elif v == TipoDuracion.semanal and dias > 7:
                raise ValueError('Una póliza semanal no puede durar más de 7 días')
            elif v == TipoDuracion.mensual and dias > 31:
                raise ValueError('Una póliza mensual no puede durar más de 31 días')
            elif v == TipoDuracion.trimestral and dias > 92:
                raise ValueError('Una póliza trimestral no puede durar más de 92 días')
            elif v == TipoDuracion.semestral and dias > 183:
                raise ValueError('Una póliza semestral no puede durar más de 183 días')
            elif v == TipoDuracion.anual and dias > 366:
                raise ValueError('Una póliza anual no puede durar más de 366 días')
        return v


class PolizaUpdate(BaseModel):
    """Esquema para actualizar una póliza existente."""
    cliente_id: Optional[UUID] = None
    corredor_id: Optional[int] = None
    tipo_seguro_id: Optional[int] = None
    carpeta: Optional[str] = None
    numero_poliza: Optional[str] = None
    endoso: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    fecha_emision: Optional[date] = None
    estado_poliza: Optional[str] = None
    forma_pago: Optional[str] = None
    tipo_endoso: Optional[str] = None
    moneda_id: Optional[int] = None
    suma_asegurada: Optional[float] = Field(None, gt=0)
    prima: Optional[float] = Field(None, gt=0)
    comision: Optional[float] = None
    cuotas: Optional[int] = Field(None, ge=1)
    observaciones: Optional[str] = None
    tipo_duracion: Optional[TipoDuracion] = None


class Poliza(PolizaBase):
    """Esquema para leer una póliza."""
    id: int
    
    class Config:
        from_attributes = True


class PolizaDetalle(Poliza):
    """Esquema detallado de póliza con información relacionada."""
    cliente_rel: Dict = Field(..., alias="cliente", description="Información del cliente")
    corredor_rel: Optional[Dict] = Field(None, alias="corredor", description="Información del corredor")
    tipo_seguro_rel: Dict = Field(..., alias="tipo_seguro", description="Información del tipo de seguro")
    moneda_rel: Optional[Dict] = Field(None, alias="moneda", description="Información de la moneda")

    @field_validator('cliente_rel', mode='before')
    def extract_cliente(cls, v):
        if hasattr(v, '__dict__'):
            return {
                'id': str(v.id),
                'nombres': v.nombres,
                'apellidos': v.apellidos,
                'numero_documento': v.numero_documento
            }
        return v

    @field_validator('corredor_rel', mode='before')
    def extract_corredor(cls, v):
        if hasattr(v, '__dict__'):
            return {
                'numero': v.numero,
                'nombres': v.nombres,
                'apellidos': v.apellidos
            }
        return v

    @field_validator('tipo_seguro_rel', mode='before')
    def extract_tipo_seguro(cls, v):
        if hasattr(v, '__dict__'):
            return {
                'id': v.id,
                'codigo': v.codigo,
                'nombre': v.nombre,
                'categoria': v.categoria
            }
        return v

    @field_validator('moneda_rel', mode='before')
    def extract_moneda(cls, v):
        if hasattr(v, '__dict__'):
            return {
                'id': v.id,
                'codigo': v.codigo,
                'nombre': v.nombre,
                'simbolo': v.simbolo
            }
        return v

    class Config:
        from_attributes = True
        populate_by_name = True
