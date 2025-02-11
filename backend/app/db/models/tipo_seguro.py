from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base_class import Base


def get_utc_now():
    """Función helper para obtener el tiempo UTC actual"""
    return datetime.now(timezone.utc)


class TipoSeguro(Base):
    """Modelo para la tabla tipos_de_seguros."""

    __tablename__ = "tipos_de_seguros"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    es_default = Column(Boolean, default=False)
    esta_activo = Column(Boolean, default=True)
    categoria = Column(String(30), nullable=False)
    cobertura = Column(Text, nullable=False)
    vigencia_default = Column(Integer, default=1)
    aseguradora_id = Column(Integer, ForeignKey("aseguradoras.id"), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), default=get_utc_now)
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now
    )

    # Relaciones
    aseguradora_rel = relationship("Aseguradora", back_populates="tipos_seguros")
    movimientos = relationship("MovimientoVigencia", back_populates="tipo_seguro_rel")
