from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import UUID4, BaseModel, Field, field_validator

# Definición de constantes
ESTADOS_POLIZA = Literal["activa", "vencida", "cancelada", "renovada"]
FORMAS_PAGO = Literal["contado", "financiado", "tarjeta", "transferencia"]
TIPOS_ENDOSO = Literal[
    "inclusión", "exclusión", "modificación", "cancelación", "renovación"
]


def to_lower(s: str) -> str:
    """Convierte una cadena a minúsculas."""
    return s.lower()


class MovimientoVigenciaBase(BaseModel):
    """Modelo base para movimientos de vigencia con validaciones y documentación."""

    cliente_id: UUID4 = Field(..., description="ID del cliente asociado al movimiento")
    corredor_id: Optional[int] = Field(
        None, description="ID del corredor que gestiona la póliza"
    )
    tipo_seguro_id: int = Field(..., description="ID del tipo de seguro")
    aseguradora_id: int = Field(
        ..., description="ID de la aseguradora que emite la póliza"
    )
    carpeta: Optional[str] = Field(
        None, description="Número de carpeta interno", max_length=50
    )
    numero_poliza: str = Field(
        ..., description="Número de póliza", min_length=5, max_length=50
    )
    endoso: Optional[str] = Field(None, description="Número de endoso", max_length=50)
    fecha_inicio: date = Field(..., description="Fecha de inicio de la vigencia")
    fecha_vencimiento: date = Field(
        ..., description="Fecha de vencimiento de la vigencia"
    )
    fecha_emision: Optional[date] = Field(
        None, description="Fecha de emisión de la póliza"
    )
    estado_poliza: ESTADOS_POLIZA = Field(
        default="activa", description="Estado actual de la póliza"
    )
    forma_pago: Optional[FORMAS_PAGO] = Field(
        None, description="Forma de pago de la póliza"
    )
    tipo_endoso: Optional[TIPOS_ENDOSO] = Field(
        None, description="Tipo de endoso si aplica"
    )
    moneda_id: Optional[int] = Field(None, description="ID de la moneda")
    suma_asegurada: Decimal = Field(..., ge=0, description="Monto asegurado")
    prima: Decimal = Field(..., ge=0, description="Prima del seguro")
    comision: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Porcentaje de comisión"
    )
    cuotas: Optional[int] = Field(None, ge=1, le=36, description="Número de cuotas")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")

    @field_validator("fecha_vencimiento")
    def validar_fecha_vencimiento(cls, v, values):
        if "fecha_inicio" in values and v <= values["fecha_inicio"]:
            raise ValueError(
                "La fecha de vencimiento debe ser posterior a la fecha de inicio"
            )
        return v

    @field_validator("carpeta", "numero_poliza", "endoso")
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        from_attributes = True


class MovimientoVigenciaCreate(MovimientoVigenciaBase):
    """Modelo para crear un nuevo movimiento de vigencia."""

    creado_por_id: int = Field(..., description="ID del usuario que crea el registro")


class MovimientoVigenciaUpdate(MovimientoVigenciaBase):
    """Modelo para actualizar un movimiento de vigencia existente."""

    cliente_id: Optional[UUID4] = None
    corredor_id: Optional[int] = None
    tipo_seguro_id: Optional[int] = None
    aseguradora_id: Optional[int] = None
    carpeta: Optional[str] = Field(None, max_length=50)
    numero_poliza: Optional[str] = Field(None, min_length=5, max_length=50)
    endoso: Optional[str] = Field(None, max_length=50)
    fecha_inicio: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    fecha_emision: Optional[date] = None
    estado_poliza: Optional[ESTADOS_POLIZA] = None
    forma_pago: Optional[FORMAS_PAGO] = None
    tipo_endoso: Optional[TIPOS_ENDOSO] = None
    moneda_id: Optional[int] = None
    suma_asegurada: Optional[Decimal] = Field(None, ge=0)
    prima: Optional[Decimal] = Field(None, ge=0)
    comision: Optional[Decimal] = Field(None, ge=0, le=100)
    cuotas: Optional[int] = Field(None, ge=1, le=36)
    observaciones: Optional[str] = None
    modificado_por_id: int = Field(
        ..., description="ID del usuario que modifica el registro"
    )


class MovimientoVigencia(MovimientoVigenciaBase):
    """Modelo completo de movimiento de vigencia con campos adicionales."""

    id: int
    fecha_creacion: datetime = Field(..., description="Fecha de creación del registro")
    fecha_actualizacion: Optional[datetime] = Field(
        None, description="Última fecha de actualización"
    )
    creado_por_id: int = Field(..., description="ID del usuario que creó el registro")
    modificado_por_id: Optional[int] = Field(
        None, description="ID del usuario que modificó el registro"
    )

    class Config:
        from_attributes = True
        alias_generator = to_lower


class MovimientoVigenciaWithRelations(MovimientoVigencia):
    """Modelo de movimiento de vigencia con sus relaciones incluidas."""

    cliente: Optional["Cliente"] = None
    corredor: Optional["Corredor"] = None
    tipo_seguro: Optional["TipoSeguro"] = None
    aseguradora: Optional["Aseguradora"] = None
    moneda: Optional["Moneda"] = None


# Las referencias a otros modelos se definen como strings para evitar importaciones circulares
Cliente = "Cliente"
Corredor = "Corredor"
TipoSeguro = "TipoSeguro"
Aseguradora = "Aseguradora"
Moneda = "Moneda"
