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
from ..viewmodels.movimiento_vigencia_viewmodel import MovimientoVigenciaViewModel
from ..viewmodels.login_viewmodel import LoginViewModel
import logging

# Configurar logging
logger = logging.getLogger(__name__)

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
        try:
            # Primero verificar si ya hay una instancia registrada
            if tipo_interfaz in self._instancias:
                return self._instancias[tipo_interfaz]
                
            # Si no hay instancia, verificar si hay una fábrica
            if tipo_interfaz in self._fabricas:
                try:
                    instancia = self._fabricas[tipo_interfaz]()
                    self._instancias[tipo_interfaz] = instancia
                    return instancia
                except Exception as e:
                    import traceback
                    logger.error(f"Error al crear la instancia de {tipo_interfaz.__name__} usando fábrica: {str(e)}")
                    logger.debug(traceback.format_exc())
                    raise
                
            # Si no hay registro, intentar resolver manualmente basado en el tipo
            if tipo_interfaz == NetworkManager:
                instancia = NetworkManager(os.getenv("API_URL", "http://localhost:8000"))
                self._instancias[tipo_interfaz] = instancia
                return instancia
            elif tipo_interfaz == AuthService:
                # Para AuthService, primero resolver NetworkManager
                network_manager = self.resolver(NetworkManager)
                instancia = AuthService(network_manager)
                self._instancias[tipo_interfaz] = instancia
                return instancia
            elif tipo_interfaz == CorredorViewModel:
                # Para CorredorViewModel, primero resolver NetworkManager
                network_manager = self.resolver(NetworkManager)
                instancia = CorredorViewModel(network_manager)
                self._instancias[tipo_interfaz] = instancia
                return instancia
            elif tipo_interfaz == MovimientoVigenciaViewModel:
                # Para MovimientoVigenciaViewModel, primero resolver NetworkManager
                network_manager = self.resolver(NetworkManager)
                instancia = MovimientoVigenciaViewModel(network_manager)
                self._instancias[tipo_interfaz] = instancia
                return instancia
            elif tipo_interfaz == LoginViewModel:
                # Para LoginViewModel, primero resolver AuthService
                auth_service = self.resolver(AuthService)
                instancia = LoginViewModel(auth_service)
                self._instancias[tipo_interfaz] = instancia
                return instancia
                
            # Si llegamos aquí, no se pudo resolver el tipo
            raise ValueError(f"No se encontró registro para {tipo_interfaz.__name__}")
                
        except Exception as e:
            if not isinstance(e, ValueError):
                import traceback
                logger.error(f"Error resolviendo dependencia {tipo_interfaz.__name__}: {str(e)}")
                logger.debug(traceback.format_exc())
            raise


# Instancia global del contenedor
contenedor = ContenedorDI()

# Configuración de la URL de la API
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Crear fábricas para servicios
def crear_network_manager():
    return NetworkManager(API_URL)

def crear_auth_service():
    network_manager = contenedor.resolver(NetworkManager)
    return AuthService(network_manager)

def crear_corredor_viewmodel():
    network_manager = contenedor.resolver(NetworkManager)
    return CorredorViewModel(network_manager)

def crear_movimiento_viewmodel():
    network_manager = contenedor.resolver(NetworkManager)
    return MovimientoVigenciaViewModel(network_manager)

def crear_login_viewmodel():
    auth_service = contenedor.resolver(AuthService)
    return LoginViewModel(auth_service)

# Registrar fábricas para servicios que necesiten crearse bajo demanda
contenedor.registrar_fabrica(NetworkManager, crear_network_manager)
contenedor.registrar_fabrica(AuthService, crear_auth_service)
contenedor.registrar_fabrica(CorredorViewModel, crear_corredor_viewmodel)
contenedor.registrar_fabrica(MovimientoVigenciaViewModel, crear_movimiento_viewmodel)
contenedor.registrar_fabrica(LoginViewModel, crear_login_viewmodel)
