from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base_class import Base


class MovimientoVigencia(Base):
    """Modelo para la tabla movimientos_vigencias."""

    __tablename__ = "movimientos_vigencias"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    corredor_id = Column(Integer, ForeignKey("corredores.numero"))
    tipo_seguro_id = Column(Integer, ForeignKey("tipos_de_seguros.id"), nullable=False)
    carpeta = Column(String(100))
    numero_poliza = Column(String(100), nullable=False, unique=True)
    endoso = Column(String(100))
    fecha_inicio = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    fecha_emision = Column(Date)
    estado_poliza = Column(String(20), default="activa")
    forma_pago = Column(String(20))
    tipo_endoso = Column(String(50))
    moneda_id = Column(Integer, ForeignKey("monedas.id"))
    suma_asegurada = Column(Float, nullable=False)
    prima = Column(Float, nullable=False)
    comision = Column(Float)
    cuotas = Column(Integer)
    observaciones = Column(String(500))

    # Relaciones
    cliente_rel = relationship("Cliente", back_populates="movimientos_vigencias")
    corredor_rel = relationship("Corredor", back_populates="movimientos")
    tipo_seguro_rel = relationship("TipoSeguro", back_populates="movimientos")
    moneda_rel = relationship("Moneda", back_populates="movimientos")
