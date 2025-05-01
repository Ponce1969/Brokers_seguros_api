"""Utilidades para validar y convertir IDs en diferentes formatos.

Este módulo contiene funciones para validar y convertir entre diferentes 
formatos de IDs, como UUIDs y enteros.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Expresión regular para validar UUIDs
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', 
    re.IGNORECASE
)


def is_uuid(id_value) -> bool:
    """Determina si un valor es un UUID válido.
    
    Args:
        id_value: El valor a verificar
        
    Returns:
        bool: True si es un UUID válido, False en caso contrario
    """
    if not id_value:
        return False
        
    if not isinstance(id_value, str):
        return False
        
    return bool(UUID_PATTERN.match(id_value))


def is_numeric_id(id_value) -> bool:
    """Determina si un valor es un ID numérico válido.
    
    Args:
        id_value: El valor a verificar
        
    Returns:
        bool: True si es un ID numérico válido, False en caso contrario
    """
    if id_value is None:
        return False
        
    try:
        # Intentar convertir a entero y verificar que sea positivo
        num_id = int(id_value)
        return num_id > 0
    except (ValueError, TypeError):
        return False


def ensure_uuid_string(id_value) -> str:
    """Asegura que un ID sea una cadena UUID válida.
    
    Args:
        id_value: El valor a convertir
        
    Returns:
        str: El UUID como cadena si es válido
        
    Raises:
        ValueError: Si el valor no puede convertirse a un UUID válido
    """
    if not id_value:
        raise ValueError("ID no puede ser nulo o vacío")
        
    # Si ya es un UUID válido, devolverlo como está
    if is_uuid(id_value):
        return id_value
        
    raise ValueError(f"El valor '{id_value}' no es un UUID válido")


def ensure_numeric_id(id_value) -> int:
    """Asegura que un ID sea un entero válido.
    
    Args:
        id_value: El valor a convertir
        
    Returns:
        int: El ID como entero si es válido
        
    Raises:
        ValueError: Si el valor no puede convertirse a un entero válido
    """
    if id_value is None:
        raise ValueError("ID no puede ser nulo")
        
    try:
        num_id = int(id_value)
        if num_id <= 0:
            raise ValueError(f"ID numérico debe ser positivo: {num_id}")
        return num_id
    except (ValueError, TypeError):
        raise ValueError(f"El valor '{id_value}' no puede convertirse a ID numérico")


def get_id_for_api_call(id_value, endpoint_type):
    """Devuelve el ID en el formato adecuado para el tipo de endpoint.
    
    Args:
        id_value: El ID a formatear
        endpoint_type: El tipo de endpoint ('cliente', 'corredor', etc.)
        
    Returns:
        El ID en el formato adecuado para el endpoint
        
    Raises:
        ValueError: Si el ID no puede convertirse al formato adecuado
    """
    if endpoint_type == 'cliente':
        # Los endpoints de cliente esperan UUIDs
        return ensure_uuid_string(id_value)
    elif endpoint_type in ['corredor', 'tipo_documento']:
        # Los endpoints de corredor y tipo_documento esperan IDs numéricos
        return ensure_numeric_id(id_value)
    else:
        # Para otros tipos, intentar determinar automáticamente
        if is_uuid(id_value):
            return id_value
        elif is_numeric_id(id_value):
            return int(id_value)
        else:
            raise ValueError(f"Formato de ID no válido para endpoint {endpoint_type}: {id_value}")
