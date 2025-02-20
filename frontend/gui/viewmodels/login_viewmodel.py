"""
ViewModel para la lógica de login
"""

import logging
from typing import Optional, Tuple
from ..services.auth_service import AuthService

# Configurar logging
logger = logging.getLogger(__name__)

class LoginViewModel:
    """ViewModel para manejar la lógica de login"""
    
    def __init__(self, auth_service: AuthService):
        """
        Inicializa el ViewModel
        
        Args:
            auth_service: Servicio de autenticación
        """
        self.auth_service = auth_service
        self.token_data: Optional[dict] = None

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

    async def login(self, email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
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
            success, message, data = await self.auth_service.login(email, password)
            
            if success:
                logger.info("✅ Login exitoso")
                self.token_data = data
                return True, "Login exitoso", data
            else:
                logger.warning(f"❌ Login fallido: {message}")
                return False, message, None
                
        except Exception as e:
            logger.error(f"❌ Error en login: {str(e)}")
            return False, f"Error en login: {str(e)}", None

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
