from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


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
    rut: Optional[str] = Field(
        None,
        min_length=8,
        max_length=12,
        description="RUT de la aseguradora"
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

    @field_validator('nombre', 'rut', 'telefono', 'direccion')
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        from_attributes = True


class AseguradoraCreate(AseguradoraBase):
    """Modelo para crear una nueva aseguradora."""
    pass


class AseguradoraUpdate(AseguradoraBase):
    """Modelo para actualizar los datos de una aseguradora existente."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    rut: Optional[str] = Field(None, min_length=8, max_length=12)
    telefono: Optional[str] = Field(None, min_length=8, max_length=20)
    direccion: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    pagina_web: Optional[HttpUrl] = None
    esta_activa: Optional[bool] = None
    observaciones: Optional[str] = None


class Aseguradora(AseguradoraBase):
    """Modelo completo de aseguradora con campos adicionales."""

    id: int
    fecha_creacion: datetime = Field(
        ...,
        description="Fecha de creación del registro"
    )
    fecha_actualizacion: Optional[datetime] = Field(
        None,
        description="Última fecha de actualización"
    )
    tipos_seguro_count: Optional[int] = Field(
        0,
        description="Cantidad de tipos de seguro ofrecidos"
    )
    movimientos_count: Optional[int] = Field(
        0,
        description="Cantidad de movimientos registrados"
    )

    class Config:
        from_attributes = True
        alias_generator = to_lower


class AseguradoraWithRelations(Aseguradora):
    """Modelo de aseguradora con sus relaciones incluidas."""

    tipos_seguro: List["TipoSeguro"] = Field(default_factory=list)
    movimientos: List["MovimientoVigencia"] = Field(default_factory=list)


# Las referencias a otros modelos se definen como strings para evitar importaciones circulares
TipoSeguro = "TipoSeguro"
MovimientoVigencia = "MovimientoVigencia"
