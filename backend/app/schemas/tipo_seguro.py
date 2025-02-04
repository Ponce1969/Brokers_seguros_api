from pydantic import BaseModel

class TipoSeguroBase(BaseModel):
    categoria: str
    cobertura: str
    vigencia_default: int = 1
    aseguradora_id: int

class TipoSeguroCreate(TipoSeguroBase):
    pass

class TipoSeguroUpdate(TipoSeguroBase):
    pass

class TipoSeguro(TipoSeguroBase):
    id: int

    class Config:
        from_attributes = True
