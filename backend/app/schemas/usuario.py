from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    username: str
    is_active: bool = True
    is_superuser: bool = False
    role: str = "user"
    comision_porcentaje: float = 0.0
    telefono: Optional[str] = None
    corredor_numero: Optional[int] = None

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(UsuarioBase):
    password: Optional[str] = None

class Usuario(UsuarioBase):
    id: int
    fecha_creacion: datetime
    fecha_modificacion: datetime

    class Config:
        from_attributes = True

class UsuarioInDB(Usuario):
    hashed_password: str