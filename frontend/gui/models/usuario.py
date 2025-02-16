"""
Modelo de datos para Usuario
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Usuario:
    """
    Clase que representa un usuario/corredor en el sistema
    """

    username: str = ""
    email: str = ""
    nombres: str = ""  # Cambiado de nombre
    apellidos: str = ""  # Cambiado de apellido
    is_active: bool = True
    is_superuser: bool = False
    role: str = "corredor"  # Roles: "corredor", "admin", etc.
    corredor_numero: Optional[int] = None
    comision_porcentaje: float = 0.0
    telefono: Optional[str] = None
    movil: Optional[str] = None  # Nuevo campo
    documento: Optional[str] = None  # Cédula o RUT
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    fecha_alta: Optional[datetime] = None  # Nuevo campo
    fecha_baja: Optional[datetime] = None  # Nuevo campo
    matricula: Optional[str] = None  # Nuevo campo
    especializacion: Optional[str] = None  # Nuevo campo
    fecha_creacion: Optional[datetime] = None
    fecha_modificacion: Optional[datetime] = None
    id: Optional[int] = None

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario"""
        return f"{self.nombres} {self.apellidos}".strip()

    @property
    def es_corredor(self) -> bool:
        """Indica si el usuario es un corredor"""
        return self.role == "corredor"

    def dict(self) -> dict:
        """Convierte el objeto a un diccionario"""
        return {
            "username": self.username,
            "email": self.email,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "role": self.role,
            "corredor_numero": self.corredor_numero,
            "comision_porcentaje": self.comision_porcentaje,
            "telefono": self.telefono,
            "movil": self.movil,
            "documento": self.documento,
            "direccion": self.direccion,
            "localidad": self.localidad,
            "fecha_alta": self.fecha_alta,
            "fecha_baja": self.fecha_baja,
            "matricula": self.matricula,
            "especializacion": self.especializacion,
            "id": self.id,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Usuario":
        """Crea una instancia de Usuario desde un diccionario"""
        # Asegurarse de que solo se usen los campos definidos en la clase
        campos_validos = {
            "username",
            "email",
            "nombres",
            "apellidos",
            "is_active",
            "is_superuser",
            "role",
            "corredor_numero",
            "comision_porcentaje",
            "telefono",
            "movil",
            "documento",
            "direccion",
            "localidad",
            "fecha_alta",
            "fecha_baja",
            "matricula",
            "especializacion",
            "fecha_creacion",
            "fecha_modificacion",
            "id",
        }
        datos_filtrados = {k: v for k, v in datos.items() if k in campos_validos}

        # Convertir fechas si están en formato string
        for campo_fecha in [
            "fecha_alta",
            "fecha_baja",
            "fecha_creacion",
            "fecha_modificacion",
        ]:
            if campo_fecha in datos_filtrados and isinstance(
                datos_filtrados[campo_fecha], str
            ):
                datos_filtrados[campo_fecha] = datetime.fromisoformat(
                    datos_filtrados[campo_fecha].replace("Z", "+00:00")
                )

        return cls(**datos_filtrados)

    def __str__(self) -> str:
        """Representación en string del usuario"""
        return (
            f"{self.nombre_completo} - Corredor #{self.corredor_numero or 'N/A'} "
            f"({self.role})"
        )

    def __repr__(self) -> str:
        """Representación detallada del usuario"""
        return (
            f"Usuario(username='{self.username}', email='{self.email}', "
            f"nombres='{self.nombres}', apellidos='{self.apellidos}', "
            f"corredor_numero={self.corredor_numero}, role='{self.role}')"
        )
