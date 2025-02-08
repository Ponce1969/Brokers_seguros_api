from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


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
    fecha_alta: date


class CorredorUpdate(CorredorBase):
    fecha_baja: Optional[date] = None


class Corredor(CorredorBase):
    numero: int
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None

    class Config:
        from_attributes = True
