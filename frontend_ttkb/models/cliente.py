"""
Modelo de Cliente

Este modelo representa a un cliente en el sistema, perfectamente alineado
con la estructura que devuelve el backend.
"""

from dataclasses import dataclass, field, fields
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
    fecha_registro: Optional[datetime] = None
    
    # Alias para compatibilidad con vistas
    @property
    def nombre(self) -> str:
        """
        Alias de nombres para compatibilidad con vistas anteriores.
        """
        return self.nombres
        
    @property
    def email(self) -> str:
        """
        Alias de mail para compatibilidad con vistas anteriores.
        """
        return self.mail or ""
        
    @property
    def telefono(self) -> str:
        """
        Alias de telefonos para compatibilidad con vistas anteriores.
        """
        return self.telefonos or self.movil or ""
    
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
        try:
            # Crear una copia para no modificar el original
            cliente_data = data.copy()
            
            # Mapeo de campos del backend al modelo
            mappings = {
                # Mapeos directos
                "nombre": "nombres",
                "email": "mail",
                "telefono": "telefonos",
                "fecha_creacion": "fecha_registro",
                "created_at": "fecha_registro",
                # Agrega mu00e1s mapeos segu00fan sea necesario
            }
            
            # Aplicar mapeos
            for backend_field, model_field in mappings.items():
                if backend_field in cliente_data and model_field not in cliente_data:
                    cliente_data[model_field] = cliente_data.pop(backend_field)
            
            # Manejo especial de fechas
            for date_field in ['fecha_registro', 'fecha_creacion', 'fecha_modificacion', 'fecha_nacimiento']:
                if date_field in cliente_data and cliente_data[date_field] and isinstance(cliente_data[date_field], str):
                    try:
                        # Intentar convertir de string ISO a objeto datetime
                        date_str = cliente_data[date_field].replace('Z', '+00:00')
                        cliente_data[date_field] = datetime.fromisoformat(date_str)
                    except (ValueError, TypeError):
                        # Mantener como string si no se puede convertir
                        logger.warning(f"No se pudo convertir la fecha: {cliente_data[date_field]}")
            
            # Crear la instancia filtrando solo los campos conocidos
            known_fields = {f.name for f in fields(cls)}
            filtered_data = {k: v for k, v in cliente_data.items() if k in known_fields}
            
            # Convertir None a valores por defecto para campos opcionales
            for field_name in known_fields:
                if field_name not in filtered_data:
                    filtered_data[field_name] = None
        
        except Exception as e:
            logger.error(f"Error al crear Cliente desde diccionario: {str(e)}")
            raise

        
        return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia a un diccionario.
        
        Este método es útil para enviar los datos al backend
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
