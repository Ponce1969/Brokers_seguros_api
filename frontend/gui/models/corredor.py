"""
Modelo de datos para Corredor
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
import logging

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
    fecha_registro: Optional[date] = None
    activo: bool = True

    # Campos adicionales (pueden ser None)
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    documento: Optional[str] = None
    localidad: Optional[str] = None
    movil: Optional[str] = None
    observaciones: Optional[str] = None
    matricula: Optional[str] = None
    especializacion: Optional[str] = None
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None

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
            # Procesar fechas
            fecha_registro = None
            if data.get("fecha_registro"):
                try:
                    fecha_registro = datetime.strptime(data["fecha_registro"], "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Error al procesar fecha_registro: {data['fecha_registro']}")

            fecha_alta = None
            if data.get("fecha_alta"):
                try:
                    fecha_alta = datetime.strptime(data["fecha_alta"], "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Error al procesar fecha_alta: {data['fecha_alta']}")

            fecha_baja = None
            if data.get("fecha_baja"):
                try:
                    fecha_baja = datetime.strptime(data["fecha_baja"], "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Error al procesar fecha_baja: {data['fecha_baja']}")

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

    def actualizar(self, datos: dict) -> None:
        """
        Actualiza los datos del corredor

        Args:
            datos: Diccionario con los datos a actualizar
        """
        for campo, valor in datos.items():
            if hasattr(self, campo):
                if campo in ["fecha_registro", "fecha_alta", "fecha_baja"] and valor:
                    if isinstance(valor, str):
                        setattr(self, campo, datetime.strptime(valor, "%Y-%m-%d").date())
                    else:
                        setattr(self, campo, valor)
                else:
                    setattr(self, campo, valor)
