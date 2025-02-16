"""
Contiene funciones relacionadas con la autenticación y seguridad,
como el hash de contraseñas y la verificación de tokens JWT.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from .config import settings

# El algoritmo se obtiene de la configuración

# Configuración del contexto de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Genera un hash bcrypt para la contraseña proporcionada.

    Args:
        password: La contraseña en texto plano

    Returns:
        str: El hash de la contraseña
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.

    Args:
        plain_password: La contraseña en texto plano a verificar
        hashed_password: El hash de la contraseña almacenado

    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_user_password_hash(password: Optional[str] = None) -> Optional[str]:
    """
    Función de utilidad para obtener el hash de la contraseña de un usuario.
    Si no se proporciona contraseña, retorna None.

    Args:
        password: La contraseña en texto plano (opcional)

    Returns:
        Optional[str]: El hash de la contraseña o None si no se proporcionó contraseña
    """
    if password:
        return get_password_hash(password)


def create_access_token(
    subject: int | str, expires_delta: timedelta | None = None
) -> str:
    """
    Genera un token JWT de acceso.

    Args:
        subject: ID del usuario u otro identificador
        expires_delta: Tiempo de expiración opcional

    Returns:
        str: Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
