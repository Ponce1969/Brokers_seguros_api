from typing import Optional, List
from pydantic import BaseModel, EmailStr, UUID4, Field, constr
from datetime import date, datetime

class ClienteBase(BaseModel):
    nombres: constr(min_length=2, max_length=100) = Field(..., description="Nombres del cliente")
    apellidos: constr(min_length=2, max_length=100) = Field(..., description="Apellidos del cliente")
    tipo_documento_id: int = Field(..., description="ID del tipo de documento")
    numero_documento: constr(min_length=5, max_length=20) = Field(..., description="Número de documento del cliente")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento del cliente")
    direccion: constr(min_length=5, max_length=200) = Field(..., description="Dirección completa del cliente")
    localidad: Optional[constr(max_length=100)] = Field(None, description="Localidad del cliente")
    telefonos: constr(min_length=8, max_length=50) = Field(..., description="Teléfonos de contacto")
    movil: constr(min_length=8, max_length=50) = Field(..., description="Número de celular")
    mail: EmailStr = Field(..., description="Correo electrónico del cliente")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")

class ClienteCreate(ClienteBase):
    creado_por_id: int = Field(..., description="ID del usuario que crea el registro")
    modificado_por_id: int = Field(..., description="ID del usuario que modifica el registro")

class ClienteUpdate(ClienteBase):
    nombres: Optional[constr(min_length=2, max_length=100)] = None
    apellidos: Optional[constr(min_length=2, max_length=100)] = None
    tipo_documento_id: Optional[int] = None
    numero_documento: Optional[constr(min_length=5, max_length=20)] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[constr(min_length=5, max_length=200)] = None
    localidad: Optional[constr(max_length=100)] = None
    telefonos: Optional[constr(min_length=8, max_length=50)] = None
    movil: Optional[constr(min_length=8, max_length=50)] = None
    mail: Optional[EmailStr] = None
    observaciones: Optional[str] = None
    modificado_por_id: int = Field(..., description="ID del usuario que modifica el registro")

class Cliente(ClienteBase):
    id: UUID4
    numero_cliente: int = Field(..., description="Número único de cliente")
    creado_por_id: int
    modificado_por_id: int
    fecha_creacion: datetime
    fecha_modificacion: datetime
    corredores_count: Optional[int] = Field(0, description="Cantidad de corredores asignados")
    polizas_count: Optional[int] = Field(0, description="Cantidad de pólizas activas")

    class Config:
        from_attributes = True

class ClienteWithRelations(Cliente):
    tipo_documento: "TipoDocumento"
    corredores: List["Corredor"] = []
    movimientos: List["MovimientoVigencia"] = []
    creado_por: "Usuario"
    modificado_por: "Usuario"

# Importaciones para evitar referencias circulares
from .tipo_documento import TipoDocumento
from .corredor import Corredor
from .movimiento_vigencia import MovimientoVigencia
from .usuario import Usuario

ClienteWithRelations.model_rebuild()