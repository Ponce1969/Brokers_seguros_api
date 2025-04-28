"""Modelo de datos para TipoDocumento"""

from dataclasses import dataclass, field
from typing import Optional
import logging

# Configurar logging
logger = logging.getLogger(__name__)


@dataclass
class TipoDocumento:
    """
    Modelo de datos para representar un Tipo de Documento
    """

    # Campos reflejando exactamente la estructura del backend
    id: int  # Clave primaria
    codigo: str  # Código único (ej: DNI, RUT)
    nombre: str  # Nombre completo del tipo
    descripcion: Optional[str] = field(default=None)  # Descripción adicional
    es_default: bool = field(default=False)  # Indica si es el tipo por defecto
    esta_activo: bool = field(default=True)  # Indica si está activo
    
    def __str__(self) -> str:
        """Representación en cadena para mostrar en UI"""
        return f"{self.nombre} ({self.codigo})"
        
    @classmethod
    def from_dict(cls, data: dict) -> 'TipoDocumento':
        """
        Crea una instancia desde un diccionario, útil para convertir respuestas API
        """
        try:
            return cls(
                id=data.get('id'),
                codigo=data.get('codigo', ''),
                nombre=data.get('nombre', ''),
                descripcion=data.get('descripcion'),
                es_default=data.get('es_default', False),
                esta_activo=data.get('esta_activo', True)
            )
        except Exception as e:
            logger.error(f"Error al convertir diccionario a TipoDocumento: {e}")
            # Crear una instancia vacía como fallback
            return cls(id=0, codigo='', nombre='Error de conversión')
