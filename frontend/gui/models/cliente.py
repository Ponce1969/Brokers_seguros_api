"""
Modelo de datos para Cliente
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date
import logging

# Configurar logging
logger = logging.getLogger(__name__)


@dataclass
class Cliente:
    """
    Modelo de datos para representar un Cliente
    """

    # Campos reflejando exactamente la estructura del backend
    id: str = field(default="")  # ID único del cliente
    numero_cliente: int = field(default=0)  # Número de cliente (identificador de negocio)
    nombres: str = field(default="")  # Nombres del cliente
    apellidos: str = field(default="")  # Apellidos del cliente
    tipo_documento_id: int = field(default=0)  # ID del tipo de documento
    numero_documento: str = field(default="")  # Número de documento
    fecha_nacimiento: Optional[date] = field(default=None)  # Fecha de nacimiento
    direccion: str = field(default="")  # Dirección completa
    localidad: str = field(default="")  # Localidad/Ciudad
    telefonos: str = field(default="")  # Teléfono fijo
    movil: str = field(default="")  # Teléfono móvil
    mail: str = field(default="")  # Correo electrónico
    observaciones: str = field(default="")  # Observaciones generales
    creado_por_id: int = field(default=0)  # ID del corredor que creó el cliente
    modificado_por_id: int = field(default=0)  # ID del último corredor que modificó
    fecha_creacion: Optional[datetime] = field(default=None)  # Fecha de creación
    fecha_modificacion: Optional[datetime] = field(default=None)  # Fecha de última modificación
    corredores_count: int = field(default=0)  # Cantidad de corredores asociados
    polizas_count: int = field(default=0)  # Cantidad de pólizas asociadas

    @classmethod
    def from_dict(cls, data: dict) -> "Cliente":
        """
        Crea una instancia de Cliente desde un diccionario

        Args:
            data: Diccionario con los datos del cliente

        Returns:
            Cliente: Nueva instancia de Cliente
        """
        try:
            # Crear una copia del diccionario para no modificar el original
            cliente_dict = data.copy()

            # Mapear clave 'numero' recibida del servidor a 'numero_cliente'
            if "numero" in cliente_dict:
                cliente_dict["numero_cliente"] = cliente_dict.pop("numero")

            # Mapear clave 'email' de la respuesta a 'mail'
            if "email" in cliente_dict:
                cliente_dict["mail"] = cliente_dict.pop("email")

            # Mapear clave 'telefono' de la respuesta a 'telefonos' y 'movil'
            if "telefono" in cliente_dict:
                t = cliente_dict.pop("telefono")
                cliente_dict["telefonos"] = t
                cliente_dict["movil"] = t

            # Procesar fechas si existen
            if "fecha_nacimiento" in cliente_dict and cliente_dict["fecha_nacimiento"]:
                if isinstance(cliente_dict["fecha_nacimiento"], str):
                    cliente_dict["fecha_nacimiento"] = date.fromisoformat(
                        cliente_dict["fecha_nacimiento"].split("T")[0]
                    )

            if "fecha_creacion" in cliente_dict and cliente_dict["fecha_creacion"]:
                if isinstance(cliente_dict["fecha_creacion"], str):
                    cliente_dict["fecha_creacion"] = datetime.fromisoformat(
                        cliente_dict["fecha_creacion"].replace("Z", "+00:00")
                    )

            if "fecha_modificacion" in cliente_dict and cliente_dict["fecha_modificacion"]:
                if isinstance(cliente_dict["fecha_modificacion"], str):
                    cliente_dict["fecha_modificacion"] = datetime.fromisoformat(
                        cliente_dict["fecha_modificacion"].replace("Z", "+00:00")
                    )

            # Convertir ID a string si existe y no es string
            if "id" in cliente_dict and cliente_dict["id"] is not None:
                cliente_dict["id"] = str(cliente_dict["id"])

            # Filtrar claves no reconocidas para evitar error de argumentos inesperados
            valid_keys = set(cls.__dataclass_fields__.keys())
            filtered_dict = {k: v for k, v in cliente_dict.items() if k in valid_keys}
            # Log para depuración de datos recibidos
            logger.debug(f"Creando cliente desde datos: {filtered_dict}")
            return cls(**filtered_dict)
        except Exception as e:
            logger.error(f"Error al crear Cliente desde diccionario: {e}")
            # En caso de error, crear un cliente vacío
            return cls()

    def to_dict(self) -> dict:
        """
        Convierte el objeto Cliente a un diccionario para enviar al backend

        Returns:
            dict: Diccionario con los datos del cliente
        """
        cliente_dict = {
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "tipo_documento_id": self.tipo_documento_id,
            "numero_documento": self.numero_documento,
            "direccion": self.direccion,
            "localidad": self.localidad,
            "telefonos": self.telefonos,
            "movil": self.movil,
            "mail": self.mail,
        }

        # Agregar campos opcionales solo si tienen valor
        if self.id:
            cliente_dict["id"] = self.id

        if self.numero_cliente:
            cliente_dict["numero_cliente"] = self.numero_cliente

        if self.fecha_nacimiento:
            cliente_dict["fecha_nacimiento"] = self.fecha_nacimiento.isoformat()

        if self.observaciones:
            cliente_dict["observaciones"] = self.observaciones

        # No enviamos los campos de auditoría (se generan en el backend)
        # creado_por_id, modificado_por_id, fecha_creacion, fecha_modificacion

        return cliente_dict

    @property
    def nombre_completo(self) -> str:
        """Devuelve el nombre completo del cliente para mostrar en la UI"""
        return f"{self.nombres} {self.apellidos}".strip()

    def __str__(self) -> str:
        return f"{self.nombre_completo} ({self.numero_documento})"
