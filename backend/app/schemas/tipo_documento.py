from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class TipoDocumentoBase(BaseModel):
    """Modelo base para tipos de documento con validaciones y documentación."""
    
    codigo: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Código único del tipo de documento (ej: CI, RUT, DNI)"
    )
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nombre del tipo de documento"
    )
    descripcion: Optional[str] = Field(
        None,
        description="Descripción adicional del tipo de documento"
    )
    es_default: bool = Field(
        default=False,
        description="Indica si es el tipo de documento por defecto"
    )
    esta_activo: bool = Field(
        default=True,
        description="Indica si el tipo de documento está activo"
    )

    @field_validator('codigo', 'nombre')
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        from_attributes = True


class TipoDocumentoCreate(TipoDocumentoBase):
    """Modelo para crear un nuevo tipo de documento."""
    pass


class TipoDocumentoUpdate(TipoDocumentoBase):
    """Modelo para actualizar un tipo de documento existente."""
    
    codigo: Optional[str] = Field(None, min_length=2, max_length=10)
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    descripcion: Optional[str] = None
    es_default: Optional[bool] = None
    esta_activo: Optional[bool] = None


class TipoDocumento(TipoDocumentoBase):
    """Modelo completo de tipo de documento con campos adicionales."""
    
    id: int
    clientes_count: Optional[int] = Field(
        0,
        description="Cantidad de clientes que usan este tipo de documento"
    )

    class Config:
        from_attributes = True


class TipoDocumentoWithRelations(TipoDocumento):
    """Modelo de tipo de documento con sus relaciones incluidas."""
    
    clientes: List["Cliente"] = Field(default_factory=list)


# Las referencias a otros modelos se definen como strings para evitar importaciones circulares
Cliente = "Cliente"  # Este será resuelto por Pydantic en tiempo de ejecución
