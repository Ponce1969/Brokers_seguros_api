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
    apellidos: str
    documento: str
    direccion: str
    localidad: str
    mail: str

    # Campos opcionales
    nombres: Optional[str] = None
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
        """
        Crea una instancia de Corredor desde un diccionario

        Args:
            data: Diccionario con los datos del corredor

        Returns:
            Corredor: Nueva instancia de Corredor
        """
        # Obtener y procesar el nombre completo si existe
        nombre_completo = data.get("nombre", "")
        nombres = data.get("nombres")
        apellidos = data.get("apellidos")

        # Si no hay nombres/apellidos pero hay nombre completo, dividirlo
        if not nombres and not apellidos and nombre_completo:
            try:
                partes = nombre_completo.split()
                if len(partes) > 0:
                    nombres = partes[0]
                    apellidos = " ".join(partes[1:]) if len(partes) > 1 else ""
            except Exception as e:
                logger.error(f"Error al dividir nombre completo '{nombre_completo}': {e}")
                nombres = nombre_completo
                apellidos = ""

        # Asegurar que nombres y apellidos no sean None
        nombres = nombres or ""
        apellidos = apellidos or ""

        # Manejar otros campos con sus alternativas
        mail = data.get("mail") or data.get("email") or ""
        telefonos = data.get("telefonos") or data.get("telefono") or ""

        logger.debug(f"Procesando datos del corredor: {data}")
        logger.debug(f"Nombres: {nombres}, Apellidos: {apellidos}")

        # Convertir el número a int
        try:
            numero = int(data.get("numero", 0))
        except (ValueError, TypeError):
            numero = 0

        # Procesar fechas
        def parse_date(date_str: Optional[str]) -> Optional[date]:
            if not date_str:
                return None
            try:
                # Intentar primero como datetime
                if 'T' in date_str:
                    return datetime.fromisoformat(date_str).date()
                # Luego como date
                return date.fromisoformat(date_str)
            except (ValueError, TypeError) as e:
                logger.error(f"Error al procesar fecha '{date_str}': {e}")
                return None

        return cls(
            id=int(data.get("id", 0)),
            numero=numero,
            nombres=nombres,
            apellidos=apellidos,
            documento=data.get("documento", data.get("rut", "")),
            direccion=data.get("direccion", ""),
            localidad=data.get("localidad", ""),
            telefonos=telefonos,
            movil=data.get("movil"),
            mail=mail,
            observaciones=data.get("observaciones"),
            matricula=data.get("matricula"),
            especializacion=data.get("especializacion"),
            fecha_alta=parse_date(data.get("fecha_alta")),
            fecha_baja=parse_date(data.get("fecha_baja")),
            activo=data.get("activo", True),
        )

    def to_dict(self) -> dict:
        """
        Convierte la instancia a un diccionario

        Returns:
            dict: Diccionario con los datos del corredor
        """
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
        """
        Actualiza los datos del corredor

        Args:
            datos: Diccionario con los datos a actualizar
        """
        if "numero" in datos:
            self.numero = int(datos["numero"])
        if "nombres" in datos:
            self.nombres = datos["nombres"]
        if "apellidos" in datos:
            self.apellidos = datos["apellidos"]
        if "documento" in datos:
            self.documento = datos["documento"]
        if "direccion" in datos:
            self.direccion = datos["direccion"]
        if "localidad" in datos:
            self.localidad = datos["localidad"]
        if "telefonos" in datos:
            self.telefonos = datos["telefonos"]
        if "movil" in datos:
            self.movil = datos["movil"]
        if "mail" in datos:
            self.mail = datos["mail"]
        if "observaciones" in datos:
            self.observaciones = datos["observaciones"]
        if "matricula" in datos:
            self.matricula = datos["matricula"]
        if "especializacion" in datos:
            self.especializacion = datos["especializacion"]
        if "fecha_alta" in datos and datos["fecha_alta"]:
            self.fecha_alta = (
                datetime.fromisoformat(datos["fecha_alta"]).date()
                if isinstance(datos["fecha_alta"], str)
                else datos["fecha_alta"]
            )
        if "fecha_baja" in datos and datos["fecha_baja"]:
            self.fecha_baja = (
                datetime.fromisoformat(datos["fecha_baja"]).date()
                if isinstance(datos["fecha_baja"], str)
                else datos["fecha_baja"]
            )
        if "activo" in datos:
            self.activo = datos["activo"]
