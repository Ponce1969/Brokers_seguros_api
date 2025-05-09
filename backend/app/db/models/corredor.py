from sqlalchemy import Column, Date, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base_class import Base


class Corredor(Base):
    """Modelo para la tabla corredores.
    
    Este modelo representa a los corredores de seguros en el sistema.
    Un corredor puede tener usuarios asociados con diferentes roles.
    
    Relaciones:
    - Un corredor puede tener múltiples usuarios asociados
    - Un corredor puede tener múltiples clientes asociados
    - Un corredor puede tener múltiples movimientos asociados
    """
    
    __tablename__ = "corredores"

    # Identificación
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Clave primaria técnica
    numero = Column(Integer, unique=True, index=True, nullable=False)  # Identificador de negocio
    tipo = Column(String(20), default="corredor")  # Tipo de corredor: corredor, productor, etc.
    nombres = Column(String(30))  # Nombres del corredor
    apellidos = Column(String(30), nullable=False)  # Apellidos del corredor
    documento = Column(String(20), nullable=False, unique=True)  # Número de documento

    # Datos de contacto
    direccion = Column(String(70), nullable=False)  # Dirección del corredor
    localidad = Column(String(15), nullable=False)  # Localidad de residencia
    telefonos = Column(String(20))  # Teléfono fijo
    movil = Column(String(20))  # Teléfono móvil
    mail = Column(String(40), nullable=False, unique=True)  # Correo electrónico

    # Datos adicionales
    observaciones = Column(Text)  # Observaciones adicionales
    fecha_alta = Column(Date)  # Fecha de alta del corredor
    fecha_baja = Column(Date)  # Fecha de baja del corredor (si aplica)
    matricula = Column(String(50))  # Matrícula o número de registro (opcional)
    especializacion = Column(String(100))  # Especialización del corredor (opcional)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="corredor_rel")
    clientes_asociados = relationship("ClienteCorredor", back_populates="corredor_rel")
    movimientos = relationship("MovimientoVigencia", back_populates="corredor_rel")
