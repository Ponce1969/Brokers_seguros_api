"""
Modelo de datos para Corredor
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

@dataclass
class Corredor:
    """Modelo de datos para representar un Corredor"""

    # Campos requeridos
    id: int
    numero: int
    apellidos: str
    documento: str
    mail: str

    # Campos opcionales con valores por defecto
    direccion: str = ""
    localidad: str = ""
    nombres: str = ""
    telefonos: Optional[str] = None
    movil: Optional[str] = None
    observaciones: Optional[str] = None
    matricula: Optional[str] = None
    especializacion: Optional[str] = None
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None
    activo: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "Corredor":
        """Crea una instancia de Corredor desde un diccionario"""
        # Procesar fechas
        def parse_date(date_str: Optional[str]) -> Optional[date]:
            if not date_str:
                return None
            try:
                if 'T' in date_str:
                    return datetime.fromisoformat(date_str).date()
                return date.fromisoformat(date_str)
            except (ValueError, TypeError) as e:
                logger.error(f"Error al procesar fecha '{date_str}': {e}")
                return None

        return cls(
            id=int(data.get("id", 0)),
            numero=int(data.get("numero", 0)),
            nombres=data.get("nombres", ""),
            apellidos=data.get("apellidos", ""),
            documento=data.get("documento", ""),
            direccion=data.get("direccion", ""),
            localidad=data.get("localidad", ""),
            telefonos=data.get("telefonos") or data.get("telefono"),
            movil=data.get("movil"),
            mail=data.get("mail", data.get("email", "")),
            observaciones=data.get("observaciones"),
            matricula=data.get("matricula"),
            especializacion=data.get("especializacion"),
            fecha_alta=parse_date(data.get("fecha_alta")),
            fecha_baja=parse_date(data.get("fecha_baja")),
            activo=data.get("activo", True),
        )

    def to_dict(self) -> dict:
        """Convierte la instancia a un diccionario"""
        data = {
            "id": self.id,
            "numero": self.numero,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "documento": self.documento,
            "direccion": self.direccion,
            "localidad": self.localidad,
            "telefonos": self.telefonos,
            "movil": self.movil,
            "mail": self.mail,
            "observaciones": self.observaciones,
            "matricula": self.matricula,
            "especializacion": self.especializacion,
            "fecha_alta": self.fecha_alta.isoformat() if self.fecha_alta else None,
            "fecha_baja": self.fecha_baja.isoformat() if self.fecha_baja else None,
            "activo": self.activo,
        }
        return {k: v for k, v in data.items() if v is not None}

    def actualizar(self, datos: dict) -> None:
        """Actualiza los datos del corredor"""
        for campo, valor in datos.items():
            if campo in ["fecha_alta", "fecha_baja"] and valor:
                setattr(self, campo, 
                    datetime.fromisoformat(valor).date() 
                    if isinstance(valor, str) else valor
                )
            elif campo == "numero":
                setattr(self, campo, int(valor))
            elif hasattr(self, campo):
                setattr(self, campo, valor)
