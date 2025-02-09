from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..base_class import Base

class TipoDocumento(Base):
    """Modelo para la tabla tipos_documento."""
    __tablename__ = "tipos_documento"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(50), nullable=False, unique=True)  # Ej: DNI, Pasaporte, etc.

    # Relación con clientes
    clientes = relationship("Cliente", back_populates="tipo_documento_rel")
