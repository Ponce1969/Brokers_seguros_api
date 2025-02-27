"""
Servicio para manejar la autenticación de usuarios
"""

import logging
from typing import Optional, Tuple
from urllib.parse import urlencode
from .api_service import ServicioAPI
from ..core.excepciones import ErrorAPI

# Configurar logging
logger = logging.getLogger(__name__)


class AuthService:
    """
    Clase para manejar la autenticación y gestión de sesiones de usuario
    """

    def __init__(self, servicio_api: ServicioAPI):
        """
        Inicializa el servicio de autenticación

        Args:
            servicio_api: Instancia del servicio API para comunicación con el backend
        """
        self.api = servicio_api

    async def login(
        self, email: str, password: str
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Autenticar usuario con email y contraseña

        Args:
            email: Correo electrónico del usuario
            password: Contraseña del usuario

        Returns:
            Tupla con:
            - bool: True si la autenticación fue exitosa
            - str: Mensaje descriptivo del resultado
            - dict: Datos del usuario autenticado o None si hubo error
        """
        try:
            logger.info(f"🔑 Intentando login para usuario: {email}")

            # Construir los datos del formulario como lo espera FastAPI OAuth2
            form_data = urlencode(
                {"username": email, "password": password, "grant_type": "password"}
            )

            # Hacer la petición de login
            data = await self.api.post(
                "api/v1/login/access-token",
                datos=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if not data or "access_token" not in data:
                logger.error("❌ Error: Respuesta inválida del servidor")
                return False, "Error de autenticación: Respuesta inválida", None

            self.api.establecer_token(data["access_token"])
            logger.info("✅ Usuario autenticado con éxito")
            return True, "Login exitoso", data

        except ErrorAPI as e:
            error_msg = str(e)
            if "Email o contraseña incorrectos" in error_msg:
                logger.error("❌ Credenciales inválidas")
                return False, "Email o contraseña incorrectos", None
            elif "Usuario inactivo" in error_msg:
                logger.error("❌ Usuario inactivo")
                return False, "El usuario está inactivo", None
            else:
                logger.error(f"❌ Error en login: {error_msg}")
                return False, f"Error de autenticación: {error_msg}", None

        except Exception as e:
            logger.error(f"❌ Error inesperado en login: {str(e)}")
            return False, "Error inesperado al autenticar", None

    async def logout(self) -> None:
        """
        Cierra la sesión del usuario actual
        """
        try:
            self.api.establecer_token(None)
            logger.info("👋 Sesión cerrada correctamente")
        except Exception as e:
            logger.error(f"❌ Error al cerrar sesión: {str(e)}")
            raise ErrorAPI("Error al cerrar la sesión")

    async def verificar_sesion(self) -> bool:
        """
        Verifica si la sesión actual es válida

        Returns:
            bool: True si la sesión es válida, False en caso contrario
        """
        try:
            # Intenta hacer una petición que requiera autenticación
            await self.api.get("api/v1/usuarios/me")
            logger.debug("✅ Sesión válida")
            return True
        except ErrorAPI:
            logger.info("⚠️ Sesión expirada o inválida")
            return False
        except Exception as e:
            logger.error(f"❌ Error al verificar sesión: {str(e)}")
            return False
