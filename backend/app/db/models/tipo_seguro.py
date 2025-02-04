from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..base_class import Base

class TipoSeguro(Base):
    """Modelo para la tabla tipos_de_seguros."""
    __tablename__ = "tipos_de_seguros"

    id = Column(Integer, primary_key=True)
    categoria = Column(String(30), nullable=False)  # Nueva columna para categoría (vida, automotor, hogar, etc.)
    cobertura = Column(Text, nullable=False)  # Nueva columna para descripción de la cobertura
    vigencia_default = Column(Integer, default=1)  # Nueva columna para vigencia por defecto (en años)
    aseguradora_id = Column(Integer, ForeignKey("aseguradoras.id"), nullable=False)  # Relación con la tabla Aseguradora

    # Relaciones
    aseguradora_rel = relationship("Aseguradora", back_populates="tipos_seguros")
    movimientos = relationship("MovimientoVigencia", back_populates="tipo_seguro_rel")