"""
Contenedor de Inyección de Dependencias para la aplicación
"""

import os
from typing import Dict, Type, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
from ..services.network_manager import NetworkManager
from ..services.auth_service import AuthService
from ..viewmodels.corredor_viewmodel import CorredorViewModel

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

        # Si no hay registro, intentar crear una instancia por defecto
        if tipo_interfaz == NetworkManager:
            instancia = NetworkManager(os.getenv("API_URL", "http://localhost:8000"))
            self._instancias[tipo_interfaz] = instancia
            return instancia
        elif tipo_interfaz == AuthService:
            instancia = AuthService()
            self._instancias[tipo_interfaz] = instancia
            return instancia
        elif tipo_interfaz == CorredorViewModel:
            instancia = CorredorViewModel()
            self._instancias[tipo_interfaz] = instancia
            return instancia

        raise Exception(f"No se encontró registro para {tipo_interfaz}")


# Instancia global del contenedor
contenedor = ContenedorDI()

# Configuración de la URL de la API
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Crear instancias de servicios
network_manager = NetworkManager(API_URL)
auth_service = AuthService()
corredor_viewmodel = CorredorViewModel()

# Registrar instancias de servicios
contenedor.registrar_instancia(NetworkManager, network_manager)
contenedor.registrar_instancia(AuthService, auth_service)
contenedor.registrar_instancia(CorredorViewModel, corredor_viewmodel)

# Registrar fábricas para servicios que necesiten crearse bajo demanda
def crear_network_manager():
    return NetworkManager(API_URL)

def crear_auth_service():
    return AuthService()

def crear_corredor_viewmodel():
    return CorredorViewModel()

contenedor.registrar_fabrica(NetworkManager, crear_network_manager)
contenedor.registrar_fabrica(AuthService, crear_auth_service)
contenedor.registrar_fabrica(CorredorViewModel, crear_corredor_viewmodel)
