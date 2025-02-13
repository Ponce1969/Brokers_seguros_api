from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Annotated
from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator

if TYPE_CHECKING:
    from .tipo_seguro import TipoSeguro
    from .movimiento_vigencia import MovimientoVigencia


def to_lower(s: str) -> str:
    """Convierte una cadena a minúsculas."""
    return s.lower()


class AseguradoraBase(BaseModel):
    """Modelo base para aseguradoras con validaciones y documentación."""

    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre de la aseguradora"
    )
    identificador_fiscal: Optional[str] = Field(
        None,
        min_length=8,
        max_length=12,
        description="Identificador fiscal de la aseguradora (RUT, CUIT, NIF, etc.)"
    )
    telefono: Optional[str] = Field(
        None,
        min_length=8,
        max_length=20,
        description="Teléfono de contacto"
    )
    direccion: Optional[str] = Field(
        None,
        max_length=200,
        description="Dirección física"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Correo electrónico de contacto"
    )
    pagina_web: Optional[HttpUrl] = Field(
        None,
        description="Sitio web oficial"
    )
    esta_activa: bool = Field(
        default=True,
        description="Indica si la aseguradora está activa"
    )
    observaciones: Optional[str] = Field(
        None,
        description="Notas adicionales sobre la aseguradora"
    )

    @field_validator('nombre', 'identificador_fiscal', 'telefono', 'direccion')
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    class Config:
        from_attributes = True


class AseguradoraCreate(AseguradoraBase):
    """Modelo para crear una nueva aseguradora."""
    pass


class AseguradoraUpdate(AseguradoraBase):
    """Modelo para actualizar los datos de una aseguradora existente."""
    nombre: Optional[str] = None
    identificador_fiscal: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    email: Optional[EmailStr] = None
    pagina_web: Optional[HttpUrl] = None
    esta_activa: Optional[bool] = None
    observaciones: Optional[str] = None


class Aseguradora(AseguradoraBase):
    """Modelo completo de aseguradora con campos adicionales."""

    id: Annotated[int, Field(gt=0)]
    fecha_creacion: datetime = Field(
        ...,
        description="Fecha de creación del registro"
    )
    fecha_actualizacion: Optional[datetime] = Field(
        None,
        description="Última fecha de actualización"
    )
    tipos_seguro_count: Optional[Annotated[int, Field(ge=0)]] = Field(
        0,
        description="Cantidad de tipos de seguro ofrecidos"
    )
    movimientos_count: Optional[Annotated[int, Field(ge=0)]] = Field(
        0,
        description="Cantidad de movimientos registrados"
    )

    class Config:
        from_attributes = True
        alias_generator = to_lower


class AseguradoraWithRelations(Aseguradora):
    """Modelo de aseguradora con sus relaciones incluidas."""

    tipos_seguro: List["TipoSeguro"] = Field(default_factory=list, description="Lista de tipos de seguro")
    movimientos: List["MovimientoVigencia"] = Field(default_factory=list, description="Lista de movimientos")

    class Config:
        from_attributes = True
        alias_generator = to_lower
