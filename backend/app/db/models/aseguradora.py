from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..base_class import Base

class Aseguradora(Base):
    """Modelo para la tabla aseguradoras."""
    __tablename__ = "aseguradoras"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)  # Nombre de la aseguradora
    telefono = Column(String(20))  # Teléfono de contacto
    direccion = Column(String(200))  # Dirección de la aseguradora
    email = Column(String(100))  # Correo electrónico
    pagina_web = Column(String(100))  # Página web

    # Relación con tipos de seguros
    tipos_seguros = relationship("TipoSeguro", back_populates="aseguradora_rel")
