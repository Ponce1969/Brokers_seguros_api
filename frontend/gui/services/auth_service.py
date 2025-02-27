"""
Servicio para manejar la autenticación de usuarios usando QNetworkAccessManager
"""

import logging
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from .network_manager import NetworkManager

# Configurar logging
logger = logging.getLogger(__name__)


class AuthService(QObject):
    """
    Clase para manejar la autenticación y gestión de sesiones de usuario
    """

    # Señales
    auth_success = pyqtSignal(
        dict
    )  # Emite los datos del token cuando la autenticación es exitosa
    auth_error = pyqtSignal(str)  # Emite mensaje de error cuando la autenticación falla
    session_expired = pyqtSignal()  # Emite cuando la sesión ha expirado

    def __init__(self):
        """
        Inicializa el servicio de autenticación
        """
        super().__init__()
        self.api = NetworkManager("http://localhost:8000")
        self.api.response_received.connect(self._handle_response)
        self.api.error_occurred.connect(self._handle_error)
        self.api.token_expired.connect(self.session_expired.emit)
        self._current_operation = None

    def _handle_response(self, response):
        """Maneja las respuestas del servidor"""
        try:
            if self._current_operation == "login":
                if isinstance(response, dict) and "access_token" in response:
                    logger.info("✅ Usuario autenticado con éxito")
                    self.api.set_token(response["access_token"])
                    self.auth_success.emit(response)
                else:
                    logger.error("❌ Error: Respuesta inválida del servidor")
                    self.auth_error.emit("Error de autenticación: Respuesta inválida")
            elif self._current_operation == "verify":
                logger.debug("✅ Sesión válida")
                self.auth_success.emit(response if isinstance(response, dict) else {})
        except Exception as e:
            logger.error(f"❌ Error procesando respuesta: {e}")
            self.auth_error.emit(str(e))
        finally:
            self._current_operation = None

    def _handle_error(self, error_msg: str):
        """Maneja los errores de las peticiones"""
        logger.error(f"❌ Error en operación {self._current_operation}: {error_msg}")

        if "Email o contraseña incorrectos" in error_msg:
            self.auth_error.emit("Email o contraseña incorrectos")
        elif "Usuario inactivo" in error_msg:
            self.auth_error.emit("El usuario está inactivo")
        else:
            self.auth_error.emit(f"Error de autenticación: {error_msg}")

    def login(self, email: str, password: str) -> None:
        """
        Autenticar usuario con email y contraseña

        Args:
            email: Correo electrónico del usuario
            password: Contraseña del usuario
        """
        try:
            logger.info(f"🔑 Intentando login para usuario: {email}")
            self._current_operation = "login"

            # Preparar datos para la petición
            login_data = {"username": email, "password": password}

            # Realizar petición de login
            self.api.post("api/v1/login/access-token", login_data)

        except Exception as e:
            logger.error(f"❌ Error inesperado en login: {str(e)}")
            self.auth_error.emit("Error inesperado al autenticar")

    def logout(self) -> None:
        """
        Cierra la sesión del usuario actual
        """
        try:
            self.api.set_token(None)
            logger.info("👋 Sesión cerrada correctamente")
        except Exception as e:
            logger.error(f"❌ Error al cerrar sesión: {str(e)}")
            self.auth_error.emit("Error al cerrar la sesión")

    def verificar_sesion(self) -> None:
        """
        Verifica si la sesión actual es válida
        """
        try:
            self._current_operation = "verify"
            self.api.get("api/v1/usuarios/me")
        except Exception as e:
            logger.error(f"❌ Error al verificar sesión: {str(e)}")
            self.auth_error.emit("Error al verificar la sesión")

    def get_token(self) -> Optional[str]:
        """
        Obtiene el token actual

        Returns:
            Optional[str]: Token actual o None si no hay sesión
        """
        return self.api.token
