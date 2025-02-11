from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from ..base_class import Base


def get_utc_now():
    """Función helper para obtener el tiempo UTC actual"""
    return datetime.now(timezone.utc)


class Moneda(Base):
    """Modelo para la tabla monedas."""

    __tablename__ = "monedas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), nullable=False, unique=True)  # Ej: USD, EUR
    nombre = Column(String(50), nullable=False)  # Nombre completo
    simbolo = Column(String(5), nullable=False)  # Símbolo ($, €, etc.)
    descripcion = Column(String(200))  # Descripción adicional
    es_default = Column(Boolean, default=False)  # Indica si es la moneda por defecto
    esta_activa = Column(Boolean, default=True)  # Indica si está activa
    fecha_creacion = Column(DateTime(timezone=True), default=get_utc_now)
    fecha_actualizacion = Column(
        DateTime(timezone=True), 
        default=get_utc_now, 
        onupdate=get_utc_now
    )

    # Relación con movimientos
    movimientos = relationship("MovimientoVigencia", back_populates="moneda_rel")
