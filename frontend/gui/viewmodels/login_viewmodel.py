"""
ViewModel para la lógica de login
"""

import logging
from typing import Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from ..services.network_manager import NetworkManager

# Configurar logging
logger = logging.getLogger(__name__)


class LoginViewModel(QObject):
    """ViewModel para manejar la lógica de login"""

    # Señales
    login_successful = pyqtSignal(dict)  # Emite los datos del token cuando el login es exitoso
    login_failed = pyqtSignal(str)      # Emite el mensaje de error cuando el login falla

    def __init__(self, auth_service=None):
        """
        Inicializa el ViewModel
        """
        super().__init__()
        self.token_data: Optional[dict] = None
        self.api = NetworkManager("http://localhost:8000")
        self.api.response_received.connect(self._handle_login_response)
        self.api.error_occurred.connect(self._handle_login_error)

    def validar_campos(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Valida los campos del formulario de login

        Args:
            email: Email a validar
            password: Contraseña a validar

        Returns:
            Tuple[bool, str]: (válido, mensaje de error)
        """
        if not email:
            return False, "El email es requerido"
        if not password:
            return False, "La contraseña es requerida"
        if "@" not in email:
            return False, "Email inválido"
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        return True, ""

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Realiza el proceso de login

        Args:
            email: Email del usuario
            password: Contraseña del usuario

        Returns:
            Tuple[bool, str, Optional[dict]]: (éxito, mensaje, datos del token)
        """
        try:
            logger.info(f"🔑 Intentando login para usuario: {email}")
            
            # Preparar datos para la petición
            login_data = {
                "username": email,
                "password": password
            }
            
            # Realizar petición de login
            self.api.post("api/v1/auth/login", login_data)
            
            # La respuesta será manejada por _handle_login_response
            return True, "Procesando login...", None

        except Exception as e:
            logger.error(f"❌ Error en login: {str(e)}")
            return False, f"Error en login: {str(e)}", None

    def _handle_login_response(self, response: dict):
        """Maneja la respuesta del servidor al login"""
        try:
            if "access_token" in response:
                logger.info("✅ Login exitoso")
                self.token_data = response
                self.login_successful.emit(response)
            else:
                logger.warning("❌ Respuesta de login inválida")
                self.login_failed.emit("Respuesta de login inválida")
        except Exception as e:
            logger.error(f"❌ Error procesando respuesta de login: {str(e)}")
            self.login_failed.emit(str(e))

    def _handle_login_error(self, error_msg: str):
        """Maneja los errores de login"""
        logger.error(f"❌ Error en login: {error_msg}")
        self.login_failed.emit(error_msg)

    def get_token(self) -> Optional[str]:
        """
        Obtiene el token de autenticación actual

        Returns:
            Optional[str]: Token de autenticación o None
        """
        if self.token_data and "access_token" in self.token_data:
            return self.token_data["access_token"]
        return None

    def get_user_role(self) -> str:
        """
        Obtiene el rol del usuario autenticado

        Returns:
            str: Rol del usuario ('admin' por defecto por ahora)
        """
        # TODO: Implementar obtención del rol desde el token
        return "admin"
