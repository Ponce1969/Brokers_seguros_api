"""
Modelo de Cliente

Este modelo representa a un cliente en el sistema, perfectamente alineado
con la estructura que devuelve el backend.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Cliente:
    """
    Modelo de Cliente alineado con la estructura del backend.
    
    Este modelo captura exactamente lo que el backend devuelve para que
    no haya desalineaciu00f3n entre frontend y backend.
    """
    # Campos obligatorios
    id: str = field(default="")
    nombres: str = field(default="")
    apellidos: str = field(default="")
    numero_documento: str = field(default="")
    
    # Campos opcionales
    numero_cliente: Optional[int] = None
    tipo_documento_id: Optional[int] = None
    fecha_nacimiento: Optional[str] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
    telefonos: Optional[str] = None
    movil: Optional[str] = None
    mail: Optional[str] = None
    observaciones: Optional[str] = None
    
    # Metadatos
    creado_por_id: Optional[int] = None
    modificado_por_id: Optional[int] = None
    fecha_creacion: Optional[str] = None
    fecha_modificacion: Optional[str] = None
    corredores_count: Optional[int] = 0
    polizas_count: Optional[int] = 0
    
    @property
    def nombre_completo(self) -> str:
        """
        Devuelve el nombre completo del cliente.
        
        Returns:
            El nombre completo (nombres + apellidos).
        """
        return f"{self.nombres} {self.apellidos}".strip()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cliente':
        """
        Crea una instancia de Cliente a partir de un diccionario.
        
        Este mu00e9todo maneja las diferencias en la estructura de datos
        que podru00eda haber entre diferentes endpoints o versiones de la API.
        
        Args:
            data: Diccionario con los datos del cliente.
            
        Returns:
            Una instancia de Cliente.
        """
        # Crear una copia para no modificar el original
        cliente_data = data.copy()
        
        # Manejar posibles diferencias en los nombres de campos
        # entre el backend y nuestro modelo
        if "nombre" in cliente_data and "nombres" not in cliente_data:
            cliente_data["nombres"] = cliente_data.pop("nombre")
            
        if "email" in cliente_data and "mail" not in cliente_data:
            cliente_data["mail"] = cliente_data.pop("email")
            
        if "telefono" in cliente_data and "telefonos" not in cliente_data:
            cliente_data["telefonos"] = cliente_data.pop("telefono")
        
        # Crear la instancia filtrando solo los campos conocidos
        known_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in cliente_data.items() if k in known_fields}
        
        return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia a un diccionario.
        
        Este mu00e9todo es u00fatil para enviar los datos al backend
        o para serializar a JSON.
        
        Returns:
            Un diccionario con los datos del cliente.
        """
        # Comenzar con un diccionario vacu00edo
        result = {}
        
        # Au00f1adir solo campos con valor no None
        for field_name, field_value in asdict(self).items():
            if field_value is not None:
                result[field_name] = field_value
        
        return result
