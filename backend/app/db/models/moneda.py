from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..base_class import Base


class Moneda(Base):
    """Modelo para la tabla monedas."""

    __tablename__ = "monedas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), nullable=False, unique=True)  # Ej: USD, EUR, etc.
    descripcion = Column(String(50), nullable=False)  # Descripción de la moneda

    # Relación con movimientos
    movimientos = relationship("MovimientoVigencia", back_populates="moneda_rel")
