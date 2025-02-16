from datetime import date
from enum import Enum
from typing import Dict, List, Optional
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


class EstadisticasDuracion(BaseModel):
    """Esquema para estadísticas por tipo de duración."""

    tipo_duracion: TipoDuracion
    cantidad_polizas: int
    suma_asegurada_total: float
    prima_total: float


class EstadisticasResponse(BaseModel):
    """Esquema para la respuesta de estadísticas."""

    total_polizas: int
    suma_asegurada_total: float
    prima_total: float
    por_duracion: List[EstadisticasDuracion]


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
    estado_poliza: str = Field(
        default="activa",
        description="Estado de la póliza: activa, vencida, cancelada, etc.",
    )
    forma_pago: Optional[str] = None
    tipo_endoso: Optional[str] = None
    moneda_id: Optional[int] = None
    suma_asegurada: float = Field(..., gt=0, description="Monto asegurado")
    prima: float = Field(..., gt=0, description="Prima del seguro")
    comision: Optional[float] = None
    cuotas: Optional[int] = Field(None, ge=1, description="Número de cuotas")
    observaciones: Optional[str] = None
    tipo_duracion: TipoDuracion = Field(
        default=TipoDuracion.anual, description="Tipo de duración de la póliza"
    )

    class Config:
        from_attributes = True


class PolizaCreate(PolizaBase):
    """Esquema para crear una nueva póliza."""

    @staticmethod
    @field_validator("fecha_vencimiento")
    def fecha_vencimiento_valida(v: date, values) -> date:
        return PolizaCreate.validar_fechas(
            values.get("fecha_inicio"), v, values.get("tipo_duracion")
        )

    @staticmethod
    @field_validator("comision")
    def comision_valida(v: Optional[float], values) -> Optional[float]:
        if v is not None:
            if v < 0:
                raise ValueError("La comisión no puede ser negativa")
            if "prima" in values and v > values["prima"]:
                raise ValueError("La comisión no puede ser mayor que la prima")
        return v

    @staticmethod
    @field_validator("tipo_duracion")
    def validar_duracion_fechas(v: TipoDuracion, values) -> TipoDuracion:
        return PolizaCreate.validar_fechas(
            values.get("fecha_inicio"), values.get("fecha_vencimiento"), v
        )

    @staticmethod
    def validar_fechas(
        fecha_inicio: Optional[date],
        fecha_vencimiento: Optional[date],
        tipo_duracion: Optional[TipoDuracion],
    ) -> date:
        if not fecha_inicio or not fecha_vencimiento or not tipo_duracion:
            return fecha_vencimiento  # Retorna sin validaciones si faltan valores

        dias = (fecha_vencimiento - fecha_inicio).days + 1

        limites = {
            TipoDuracion.diaria: 1,
            TipoDuracion.semanal: 7,
            TipoDuracion.mensual: 31,
            TipoDuracion.trimestral: 92,
            TipoDuracion.semestral: 183,
            TipoDuracion.anual: 366,
        }

        if dias > limites.get(tipo_duracion, 0):
            raise ValueError(
                f"Una póliza {tipo_duracion} no puede durar más de {limites[tipo_duracion]} días"
            )

        return fecha_vencimiento


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


class PolizaDetalle(Poliza):
    """Esquema detallado de póliza con información relacionada."""

    cliente_rel: Dict = Field(
        ..., alias="cliente", description="Información del cliente"
    )
    corredor_rel: Optional[Dict] = Field(
        None, alias="corredor", description="Información del corredor"
    )
    tipo_seguro_rel: Dict = Field(
        ..., alias="tipo_seguro", description="Información del tipo de seguro"
    )
    moneda_rel: Optional[Dict] = Field(
        None, alias="moneda", description="Información de la moneda"
    )

    class Config:
        populate_by_name = True
