from pydantic import BaseModel, UUID4
from datetime import date

class ClienteCorredorBase(BaseModel):
    cliente_id: UUID4
    corredor_numero: int
    fecha_asignacion: date

class ClienteCorredorCreate(ClienteCorredorBase):
    pass

class ClienteCorredorUpdate(ClienteCorredorBase):
    pass

class ClienteCorredor(ClienteCorredorBase):
    class Config:
        from_attributes = True
