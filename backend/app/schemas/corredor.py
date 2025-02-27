from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CorredorBase(BaseModel):
    nombres: Optional[str] = None
    apellidos: str
    documento: str
    direccion: str
    localidad: str
    telefonos: Optional[str] = None
    movil: Optional[str] = None
    mail: EmailStr
    observaciones: Optional[str] = None
    matricula: Optional[str] = None
    especializacion: Optional[str] = None


class CorredorCreate(CorredorBase):
    numero: int = Field(..., ge=1000, le=9999, description="Número de 4 cifras asignado por el admin")
    fecha_alta: Optional[date] = None


class CorredorUpdate(CorredorBase):
    fecha_baja: Optional[date] = None


class CorredorResponse(BaseModel):
    id: int
    numero: int
    email: str
    nombre: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_registro: Optional[date] = None
    activo: bool = True

    class Config:
        from_attributes = True


class Corredor(CorredorBase):
    numero: int = Field(..., ge=1000, le=9999, description="Número de 4 cifras asignado por el admin")
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None

    class Config:
        from_attributes = True
