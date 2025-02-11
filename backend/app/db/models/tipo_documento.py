from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from ..base_class import Base

class TipoDocumento(Base):
    """Modelo para la tabla tipos_documento."""
    __tablename__ = "tipos_documento"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), nullable=False, unique=True)  # Código único (ej: DNI, RUT)
    nombre = Column(String(50), nullable=False)  # Nombre completo
    descripcion = Column(String(200))  # Descripción adicional
    es_default = Column(Boolean, default=False)  # Indica si es el tipo por defecto
    esta_activo = Column(Boolean, default=True)  # Indica si está activo

    # Relación con clientes
    clientes = relationship("Cliente", back_populates="tipo_documento_rel")
