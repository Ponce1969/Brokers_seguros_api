"""
Contenedor de Inyección de Dependencias para la aplicación
"""

import os
import asyncio
from typing import Dict, Type, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
from ..services.api_service import ServicioAPI
from ..services.auth_service import AuthService

# Cargar variables de entorno
load_dotenv()

@dataclass
class ContenedorDI:
    """Contenedor para inyección de dependencias"""

    _instancias: Dict[Type, Any] = field(default_factory=dict)
    _fabricas: Dict[Type, Any] = field(default_factory=dict)

    def registrar_instancia(self, tipo_interfaz: Type, instancia: Any) -> None:
        """
        Registra una instancia para un tipo
        
        Args:
            tipo_interfaz: Tipo de la interfaz
            instancia: Instancia a registrar
        """
        self._instancias[tipo_interfaz] = instancia

    def registrar_fabrica(self, tipo_interfaz: Type, fabrica) -> None:
        """
        Registra una función fábrica para un tipo
        
        Args:
            tipo_interfaz: Tipo de la interfaz
            fabrica: Función fábrica que crea instancias
        """
        self._fabricas[tipo_interfaz] = fabrica

    def resolver(self, tipo_interfaz: Type) -> Any:
        """
        Resuelve una instancia para un tipo
        
        Args:
            tipo_interfaz: Tipo de la interfaz a resolver
            
        Returns:
            Any: Instancia del tipo solicitado
            
        Raises:
            Exception: Si no se encuentra registro para el tipo
        """
        if tipo_interfaz in self._instancias:
            return self._instancias[tipo_interfaz]

        if tipo_interfaz in self._fabricas:
            instancia = self._fabricas[tipo_interfaz]()
            self._instancias[tipo_interfaz] = instancia
            return instancia

        raise Exception(f"No se encontró registro para {tipo_interfaz}")


# Instancia global del contenedor
contenedor = ContenedorDI()

# Configuración de la URL de la API
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Asegurarse de que haya un event loop
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Configuración de servicios con parámetros mejorados
servicio_api = ServicioAPI(
    url_base=API_URL,
    timeout=30,  # 30 segundos de timeout
    cache_duration=5  # 5 minutos de caché
)

# Registrar instancias de servicios
contenedor.registrar_instancia(ServicioAPI, servicio_api)
contenedor.registrar_instancia(AuthService, AuthService(servicio_api))
