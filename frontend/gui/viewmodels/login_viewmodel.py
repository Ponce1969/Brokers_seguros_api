"""
ViewModel para la lógica de login
"""

import logging
from typing import Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from ..services.auth_service import AuthService

# Configurar logging
logger = logging.getLogger(__name__)


class LoginViewModel(QObject):
    """ViewModel para manejar la lógica de login"""

    # Señales
    login_successful = pyqtSignal(
        dict
    )  # Emite los datos del token cuando el login es exitoso
    login_failed = pyqtSignal(str)  # Emite el mensaje de error cuando el login falla

    def __init__(self, auth_service: AuthService):
        """
        Inicializa el ViewModel

        Args:
            auth_service: Servicio de autenticación
        """
        super().__init__()
        
        # Verificar que auth_service no sea None
        if auth_service is None:
            from ..core.di_container import contenedor
            auth_service = contenedor.resolver(AuthService)
            if auth_service is None:
                logger.error("AuthService no pudo ser resuelto por el contenedor")
                raise ValueError("AuthService no puede ser None")
                
        self.auth_service = auth_service
        self.token_data: Optional[dict] = None

        # Conectar señales del AuthService
        self.auth_service.auth_success.connect(self._handle_auth_success)
        self.auth_service.auth_error.connect(self._handle_auth_error)

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
            self.auth_service.login(email, password)
            return True, "Procesando login...", None
        except Exception as e:
            logger.error(f"❌ Error en login: {str(e)}")
            return False, f"Error en login: {str(e)}", None

    def _handle_auth_success(self, data: dict):
        """Maneja la respuesta exitosa de autenticación"""
        self.token_data = data
        self.login_successful.emit(data)

    def _handle_auth_error(self, error_msg: str):
        """Maneja los errores de autenticación"""
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
