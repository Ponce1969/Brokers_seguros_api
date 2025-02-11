from functools import wraps
from typing import Callable, List

from fastapi import HTTPException
from .roles import Role, RolePermissions

def require_permissions(required_permissions: List[str]):
    """
    Decorador para verificar si un usuario tiene los permisos necesarios
    para acceder a un endpoint.
    
    Args:
        required_permissions: Lista de permisos requeridos
        
    Raises:
        HTTPException: Si el usuario no tiene los permisos necesarios
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # El current_user siempre se pasa como kwarg por FastAPI
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=403,
                    detail="No se encontró el usuario actual"
                )
            
            # Obtener los permisos del rol del usuario
            user_permissions = RolePermissions.get_permissions(Role(current_user.role))
            
            # Verificar si el usuario tiene todos los permisos requeridos
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=403,
                    detail="No tiene los permisos necesarios para realizar esta acción"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
