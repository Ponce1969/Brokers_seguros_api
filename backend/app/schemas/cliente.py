from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated, List, Optional

from pydantic import UUID4, BaseModel, EmailStr, Field, field_validator

if TYPE_CHECKING:
    from .corredor import Corredor
    from .movimiento_vigencia import MovimientoVigencia
    from .tipo_documento import TipoDocumento
    from .usuario import Usuario


class ClienteBase(BaseModel):
    nombres: str = Field(
        ..., min_length=2, max_length=100, description="Nombres del cliente"
    )
    apellidos: str = Field(
        ..., min_length=2, max_length=100, description="Apellidos del cliente"
    )
    tipo_documento_id: Annotated[
        int, Field(gt=0, description="ID del tipo de documento")
    ]
    numero_documento: str = Field(
        ..., min_length=5, max_length=20, description="Número de documento del cliente"
    )
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento del cliente")
    direccion: str = Field(
        ..., min_length=5, max_length=200, description="Dirección completa del cliente"
    )
    localidad: Optional[str] = Field(
        None, max_length=100, description="Localidad del cliente"
    )
    telefonos: str = Field(
        ..., min_length=8, max_length=50, description="Teléfonos de contacto"
    )
    movil: str = Field(
        ..., min_length=8, max_length=50, description="Número de celular"
    )
    mail: EmailStr = Field(..., description="Correo electrónico del cliente")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")

    @field_validator(
        "nombres",
        "apellidos",
        "numero_documento",
        "direccion",
        "localidad",
        "telefonos",
        "movil",
    )
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("fecha_nacimiento")
    def validate_fecha_nacimiento(cls, v):
        if v > date.today():
            raise ValueError("La fecha de nacimiento no puede ser en el futuro")
        return v

    class Config:
        from_attributes = True


class ClienteCreate(ClienteBase):
    creado_por_id: Annotated[
        int, Field(gt=0, description="ID del usuario que crea el registro")
    ]
    modificado_por_id: Annotated[
        int, Field(gt=0, description="ID del usuario que modifica el registro")
    ]


class ClienteUpdate(ClienteBase):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    tipo_documento_id: Optional[Annotated[int, Field(gt=0)]] = None
    numero_documento: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    telefonos: Optional[str] = None
    movil: Optional[str] = None
    mail: Optional[EmailStr] = None
    observaciones: Optional[str] = None
    modificado_por_id: Annotated[
        int, Field(gt=0, description="ID del usuario que modifica el registro")
    ]


class Cliente(ClienteBase):
    id: UUID4
    numero_cliente: Annotated[int, Field(gt=0, description="Número único de cliente")]
    creado_por_id: Annotated[int, Field(gt=0)]
    modificado_por_id: Annotated[int, Field(gt=0)]
    fecha_creacion: datetime
    fecha_modificacion: datetime
    corredores_count: Optional[Annotated[int, Field(ge=0)]] = Field(
        0, description="Cantidad de corredores asignados"
    )
    polizas_count: Optional[Annotated[int, Field(ge=0)]] = Field(
        0, description="Cantidad de pólizas activas"
    )

    class Config:
        from_attributes = True


class ClienteWithRelations(Cliente):
    tipo_documento: Optional["TipoDocumento"] = Field(
        None, description="Tipo de documento del cliente"
    )
    corredores: List["Corredor"] = Field(
        default_factory=list, description="Lista de corredores asignados"
    )
    movimientos: List["MovimientoVigencia"] = Field(
        default_factory=list, description="Lista de movimientos"
    )
    creado_por: Optional["Usuario"] = Field(
        None, description="Usuario que creó el registro"
    )
    modificado_por: Optional["Usuario"] = Field(
        None, description="Usuario que modificó el registro"
    )

    class Config:
        from_attributes = True
