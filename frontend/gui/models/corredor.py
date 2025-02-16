"""
Modelo de datos para Corredor
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Corredor:
    """Modelo de datos para un corredor"""

    nombres: str
    apellidos: str
    documento: str
    direccion: str
    localidad: str
    mail: str
    telefonos: Optional[str] = None
    movil: Optional[str] = None
    observaciones: Optional[str] = None
    matricula: Optional[str] = None
    especializacion: Optional[str] = None
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None
    numero: Optional[int] = None

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del corredor"""
        return f"{self.nombres} {self.apellidos}"

    @property
    def datos_contacto(self) -> str:
        """Retorna los datos de contacto formateados"""
        contactos = []
        if self.telefonos:
            contactos.append(f"Tel: {self.telefonos}")
        if self.movil:
            contactos.append(f"Móvil: {self.movil}")
        if self.mail:
            contactos.append(f"Email: {self.mail}")
        return " | ".join(contactos)

    @property
    def estado(self) -> str:
        """Retorna el estado del corredor (activo/inactivo)"""
        return "Inactivo" if self.fecha_baja else "Activo"
