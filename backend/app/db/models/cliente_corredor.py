from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..base_class import Base


class ClienteCorredor(Base):
    """Modelo para la tabla intermedia entre clientes y corredores."""

    __tablename__ = "clientes_corredores"

    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id", ondelete="CASCADE"), primary_key=True)
    corredor_numero = Column(Integer, ForeignKey("corredores.numero"), primary_key=True)
    fecha_asignacion = Column(
        Date, default=datetime.utcnow
    )  # Opcional: fecha de asignación

    # Relaciones
    cliente_rel = relationship("Cliente", back_populates="corredores_asociados")
    corredor_rel = relationship("Corredor", back_populates="clientes_asociados")
