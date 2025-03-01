"""
Modelo de datos para Corredor
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Union
from datetime import datetime, date
import logging
import re

# Configurar logging
logger = logging.getLogger(__name__)


@dataclass
class Corredor:
    """
    Modelo de datos para representar un Corredor
    """

    # Campos requeridos
    id: int
    numero: int
    email: str
    nombre: str
    telefono: str
    direccion: str
    fecha_registro: Optional[date] = field(default=None)
    activo: bool = field(default=True)

    # Campos adicionales (pueden ser None)
    nombres: Optional[str] = field(default=None)
    apellidos: Optional[str] = field(default=None)
    documento: Optional[str] = field(default=None)
    localidad: Optional[str] = field(default=None)
    movil: Optional[str] = field(default=None)
    observaciones: Optional[str] = field(default=None)
    matricula: Optional[str] = field(default=None)
    especializacion: Optional[str] = field(default=None)
    fecha_alta: Optional[date] = field(default=None)
    fecha_baja: Optional[date] = field(default=None)

    @classmethod
    def from_dict(cls, data: dict) -> "Corredor":
        """
        Crea una instancia de Corredor desde un diccionario

        Args:
            data: Diccionario con los datos del corredor

        Returns:
            Corredor: Nueva instancia de Corredor
        """
        try:
            # Validaciones básicas
            if "email" in data and data["email"] and not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
                raise ValueError(f"Email inválido: {data['email']}")
            
            if "telefono" in data and data["telefono"] and not re.match(r"^[\d\s\+\-\(\)]+$", data["telefono"]):
                raise ValueError(f"Formato de teléfono inválido: {data['telefono']}")
            
            # Procesar fechas
            fecha_registro = None
            if data.get("fecha_registro"):
                try:
                    fecha_registro = datetime.strptime(data["fecha_registro"], "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Error al procesar fecha_registro: {data['fecha_registro']}")
                    raise ValueError(f"Formato de fecha_registro inválido: {data['fecha_registro']}")

            fecha_alta = None
            if data.get("fecha_alta"):
                try:
                    fecha_alta = datetime.strptime(data["fecha_alta"], "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Error al procesar fecha_alta: {data['fecha_alta']}")
                    raise ValueError(f"Formato de fecha_alta inválido: {data['fecha_alta']}")

            fecha_baja = None
            if data.get("fecha_baja"):
                try:
                    fecha_baja = datetime.strptime(data["fecha_baja"], "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Error al procesar fecha_baja: {data['fecha_baja']}")
                    raise ValueError(f"Formato de fecha_baja inválido: {data['fecha_baja']}")
                    
            # Validación de fechas coherentes
            if fecha_alta and fecha_baja and fecha_alta > fecha_baja:
                raise ValueError("La fecha de alta no puede ser posterior a la fecha de baja")

            # Crear instancia con los datos básicos
            return cls(
                id=int(data.get("id", 0)),
                numero=int(data.get("numero", 0)),
                email=data.get("email", ""),
                nombre=data.get("nombre", ""),
                telefono=data.get("telefono", ""),
                direccion=data.get("direccion", ""),
                fecha_registro=fecha_registro,
                activo=data.get("activo", True),
                # Campos adicionales
                nombres=data.get("nombres"),
                apellidos=data.get("apellidos"),
                documento=data.get("documento"),
                localidad=data.get("localidad"),
                movil=data.get("movil"),
                observaciones=data.get("observaciones"),
                matricula=data.get("matricula"),
                especializacion=data.get("especializacion"),
                fecha_alta=fecha_alta,
                fecha_baja=fecha_baja,
            )
        except Exception as e:
            logger.error(f"Error al crear Corredor desde diccionario: {e}")
            logger.error(f"Datos recibidos: {data}")
            raise

    def to_dict(self) -> dict:
        """
        Convierte la instancia a un diccionario

        Returns:
            dict: Diccionario con los datos del corredor
        """
        data = {
            "id": self.id,
            "numero": self.numero,
            "email": self.email,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "activo": self.activo,
            # Campos adicionales
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "documento": self.documento,
            "localidad": self.localidad,
            "movil": self.movil,
            "observaciones": self.observaciones,
            "matricula": self.matricula,
            "especializacion": self.especializacion,
            "fecha_alta": self.fecha_alta.isoformat() if self.fecha_alta else None,
            "fecha_baja": self.fecha_baja.isoformat() if self.fecha_baja else None,
        }
        return {k: v for k, v in data.items() if v is not None}
    
    def _parse_fecha(self, valor: str) -> Optional[date]:
        """
        Parsea una cadena de texto a un objeto date.
        
        Args:
            valor: Cadena de texto en formato 'YYYY-MM-DD'
            
        Returns:
            date: Objeto date o None si hubo un error
            
        Raises:
            ValueError: Si el formato de la fecha es inválido
        """
        if not valor:
            return None
            
        try:
            return datetime.strptime(valor, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Error al convertir fecha: {valor}")
            raise ValueError(f"Formato de fecha inválido: {valor}")

    def actualizar(self, datos: dict) -> None:
        """
        Actualiza los datos del corredor con validación de tipos.

        Args:
            datos: Diccionario con los datos a actualizar
        """
        for campo, valor in datos.items():
            if hasattr(self, campo):
                try:
                    # Manejar campos específicos por tipo
                    if campo in ["fecha_registro", "fecha_alta", "fecha_baja"]:
                        if valor is not None:
                            valor = self._parse_fecha(valor) if isinstance(valor, str) else valor
                            
                    elif campo in ["id", "numero"]:
                        if valor is not None and not isinstance(valor, int):
                            try:
                                valor = int(valor)
                            except (ValueError, TypeError):
                                logger.warning(f"Se esperaba un int para {campo}, pero se recibió {type(valor)}")
                                continue
                                
                    elif campo == "activo" and not isinstance(valor, bool):
                        if isinstance(valor, str):
                            valor = valor.lower() in ("true", "t", "1", "yes", "y")
                        elif isinstance(valor, int):
                            valor = bool(valor)
                        else:
                            logger.warning(f"Se esperaba un bool para {campo}, pero se recibió {type(valor)}")
                            continue
                            
                    # Validar formato de campos de texto específicos
                    elif campo == "email" and valor and not re.match(r"[^@]+@[^@]+\.[^@]+", valor):
                        raise ValueError(f"Email inválido: {valor}")
                        
                    elif campo == "telefono" and valor and not re.match(r"^[\d\s\+\-\(\)]+$", valor):
                        raise ValueError(f"Formato de teléfono inválido: {valor}")
                        
                    # Asignar el valor
                    setattr(self, campo, valor)
                    
                except Exception as e:
                    logger.error(f"Error al actualizar campo '{campo}': {e}")
                    raise
                    
        # Verificar coherencia de fechas después de actualizar
        if self.fecha_alta and self.fecha_baja and self.fecha_alta > self.fecha_baja:
            raise ValueError("La fecha de alta no puede ser posterior a la fecha de baja")
