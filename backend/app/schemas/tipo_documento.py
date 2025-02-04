from pydantic import BaseModel

class TipoDocumentoBase(BaseModel):
    descripcion: str

class TipoDocumentoCreate(TipoDocumentoBase):
    pass

class TipoDocumentoUpdate(TipoDocumentoBase):
    pass

class TipoDocumento(TipoDocumentoBase):
    id: int

    class Config:
        from_attributes = True
