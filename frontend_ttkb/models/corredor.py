"""
Modelo de Corredor

Este modelo representa a un corredor en el sistema, perfectamente alineado
con la estructura que devuelve el backend.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Corredor:
    """
    Modelo de Corredor alineado con la estructura del backend.
    
    Este modelo captura exactamente lo que el backend devuelve para que
    no haya desalineaciu00f3n entre frontend y backend.
    """
    # Campos obligatorios basados en lo que hemos visto en el backend
    id: int = field(default=0)
    numero: int = field(default=0)
    documento: str = field(default="")
    nombre: str = field(default="")  # El backend usa 'nombre' para corredores
    
    # Campos opcionales
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_registro: Optional[str] = None
    activo: bool = True
    
    # Metadatos y relaciones
    clientes_count: Optional[int] = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Corredor':
        """
        Crea una instancia de Corredor a partir de un diccionario.
        
        Args:
            data: Diccionario con los datos del corredor.
            
        Returns:
            Una instancia de Corredor.
        """
        # Crear una copia para no modificar el original
        corredor_data = data.copy()
        
        # Manejar posibles diferencias en los nombres de campos
        if "mail" in corredor_data and "email" not in corredor_data:
            corredor_data["email"] = corredor_data.pop("mail")
            
        if "telefonos" in corredor_data and "telefono" not in corredor_data:
            corredor_data["telefono"] = corredor_data.pop("telefonos")
            
        if "movil" in corredor_data and "telefono" not in corredor_data:
            corredor_data["telefono"] = corredor_data.pop("movil")
            
        if "fecha_alta" in corredor_data and "fecha_registro" not in corredor_data:
            corredor_data["fecha_registro"] = corredor_data.pop("fecha_alta")
        
        # Si tenemos nombres y apellidos separados pero no nombre completo
        if "nombres" in corredor_data and "apellidos" in corredor_data and "nombre" not in corredor_data:
            nombres = corredor_data.pop("nombres", "")
            apellidos = corredor_data.pop("apellidos", "")
            corredor_data["nombre"] = f"{nombres} {apellidos}".strip()
        
        # Crear la instancia con los campos conocidos
        known_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in corredor_data.items() if k in known_fields}
        
        return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia a un diccionario.
        
        Returns:
            Un diccionario con los datos del corredor.
        """
        # Comenzar con un diccionario vacu00edo
        result = {}
        
        # Au00f1adir solo campos con valor no None
        for field_name, field_value in asdict(self).items():
            if field_value is not None:
                result[field_name] = field_value
        
        return result
