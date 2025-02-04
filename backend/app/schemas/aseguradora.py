from pydantic import BaseModel, EmailStr

class AseguradoraBase(BaseModel):
    nombre: str
    telefono: str | None = None
    direccion: str | None = None
    email: EmailStr | None = None
    pagina_web: str | None = None

class AseguradoraCreate(AseguradoraBase):
    pass

class AseguradoraUpdate(AseguradoraBase):
    pass

class Aseguradora(AseguradoraBase):
    id: int

    class Config:
        from_attributes = True
