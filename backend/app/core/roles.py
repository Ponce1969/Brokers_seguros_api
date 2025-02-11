from enum import Enum
from typing import Set

class Role(str, Enum):
    ADMIN = "admin"
    CORREDOR = "corredor"
    ASISTENTE = "asistente"

class RolePermissions:
    """Define los permisos por rol"""
    
    PERMISSIONS = {
        Role.ADMIN: {
            "usuarios_crear",
            "usuarios_ver",
            "usuarios_editar",
            "usuarios_eliminar",
            "polizas_crear",
            "polizas_ver",
            "polizas_editar",
            "polizas_eliminar",
            "clientes_crear",
            "clientes_ver",
            "clientes_editar",
            "clientes_eliminar",
            "reportes_ver",
            "comisiones_ver",
            "comisiones_editar"
        },
        Role.CORREDOR: {
            "polizas_crear",
            "polizas_ver",
            "polizas_editar",
            "clientes_crear",
            "clientes_ver",
            "clientes_editar",
            "comisiones_ver"
        },
        Role.ASISTENTE: {
            "polizas_ver",
            "clientes_ver",
            "reportes_ver"
        }
    }

    @classmethod
    def get_permissions(cls, role: Role) -> Set[str]:
        """Obtiene los permisos para un rol específico"""
        return cls.PERMISSIONS.get(role, set())
