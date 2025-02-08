from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, UUID4, Field, field_validator


class ClienteBase(BaseModel):
    nombres: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombres del cliente"
    )
    apellidos: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Apellidos del cliente"
    )
    tipo_documento_id: int = Field(
        ...,
        description="ID del tipo de documento"
    )
    numero_documento: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Número de documento del cliente"
    )
    fecha_nacimiento: date = Field(
        ...,
        description="Fecha de nacimiento del cliente"
    )
    direccion: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Dirección completa del cliente"
    )
    localidad: Optional[str] = Field(
        None,
        max_length=100,
        description="Localidad del cliente"
    )
    telefonos: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="Teléfonos de contacto"
    )
    movil: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="Número de celular"
    )
    mail: EmailStr = Field(
        ...,
        description="Correo electrónico del cliente"
    )
    observaciones: Optional[str] = Field(
        None,
        description="Observaciones adicionales"
    )

    @field_validator('nombres', 'apellidos', 'numero_documento', 'direccion', 'localidad', 'telefonos', 'movil')
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        from_attributes = True


class ClienteCreate(ClienteBase):
    creado_por_id: int = Field(
        ...,
        description="ID del usuario que crea el registro"
    )
    modificado_por_id: int = Field(
        ...,
        description="ID del usuario que modifica el registro"
    )


class ClienteUpdate(ClienteBase):
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    tipo_documento_id: Optional[int] = None
    numero_documento: Optional[str] = Field(None, min_length=5, max_length=20)
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = Field(None, min_length=5, max_length=200)
    localidad: Optional[str] = Field(None, max_length=100)
    telefonos: Optional[str] = Field(None, min_length=8, max_length=50)
    movil: Optional[str] = Field(None, min_length=8, max_length=50)
    mail: Optional[EmailStr] = None
    observaciones: Optional[str] = None
    modificado_por_id: int = Field(
        ...,
        description="ID del usuario que modifica el registro"
    )


class Cliente(ClienteBase):
    id: UUID4
    numero_cliente: int = Field(
        ...,
        description="Número único de cliente"
    )
    creado_por_id: int
    modificado_por_id: int
    fecha_creacion: datetime
    fecha_modificacion: datetime
    corredores_count: Optional[int] = Field(
        0,
        description="Cantidad de corredores asignados"
    )
    polizas_count: Optional[int] = Field(
        0,
        description="Cantidad de pólizas activas"
    )

    class Config:
        from_attributes = True


class ClienteWithRelations(Cliente):
    tipo_documento: Optional["TipoDocumento"] = None
    corredores: List["Corredor"] = Field(default_factory=list)
    movimientos: List["MovimientoVigencia"] = Field(default_factory=list)
    creado_por: Optional["Usuario"] = None
    modificado_por: Optional["Usuario"] = None


# Las referencias a otros modelos se definen como strings para evitar importaciones circulares
TipoDocumento = "TipoDocumento"
Corredor = "Corredor"
MovimientoVigencia = "MovimientoVigencia"
Usuario = "Usuario"
