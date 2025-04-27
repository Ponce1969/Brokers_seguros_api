from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..base_class import Base


def get_utc_now():
    """Función helper para obtener el tiempo UTC actual"""
    return datetime.now(timezone.utc)


class Usuario(Base):
    """Modelo para la tabla usuarios.
    
    Este modelo representa a los usuarios del sistema. Un usuario puede tener
    diferentes roles (admin, corredor, asistente) y, dependiendo de su rol,
    puede estar asociado o no a un corredor.
    
    Relaciones:
    - Si el rol es 'corredor', debe tener un corredor_numero asociado
    - Si el rol es 'admin' o 'asistente', puede o no tener un corredor_numero
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(64), nullable=False)
    apellido = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False, unique=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(20), default="user")  # Roles: "corredor", "admin", etc.
    corredor_numero = Column(
        Integer, ForeignKey("corredores.numero"), nullable=True
    )  # Relación con corredor (usando el número visible del corredor)
    comision_porcentaje = Column(Float, default=0.0)  # Solo aplicable a corredores
    telefono = Column(String(20))  # Teléfono de contacto
    fecha_creacion = Column(DateTime(timezone=True), default=get_utc_now)
    fecha_modificacion = Column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now
    )

    # Relaciones
    clientes_creados = relationship(
        "Cliente",
        back_populates="creado_por_usuario",
        foreign_keys="Cliente.creado_por_id",
        lazy="selectin",
    )
    clientes_modificados = relationship(
        "Cliente",
        back_populates="modificado_por_usuario",
        foreign_keys="Cliente.modificado_por_id",
        lazy="selectin",
    )
    corredor_rel = relationship(
        "Corredor",
        back_populates="usuarios",
        lazy="selectin",
    )
    
    def has_permission(self, permission: str) -> bool:
        """Verifica si el usuario tiene un permiso específico basado en su rol.
        
        Args:
            permission: El permiso a verificar
            
        Returns:
            bool: True si el usuario tiene el permiso, False en caso contrario
        """
        from app.core.roles import RolePermissions
        
        if self.is_superuser:
            return True  # Los superusuarios tienen todos los permisos
            
        if not self.is_active:
            return False  # Los usuarios inactivos no tienen permisos
            
        # Verificar si el rol del usuario tiene el permiso solicitado
        return permission in RolePermissions.get_permissions(self.role)
    
    def validate_role_consistency(self) -> bool:
        """Valida que el rol del usuario sea consistente con sus relaciones.
        
        Returns:
            bool: True si el rol es consistente, False en caso contrario
        """
        from app.core.roles import Role
        
        # Si el rol es corredor, debe tener un corredor asociado
        if self.role == Role.CORREDOR and not self.corredor_numero:
            return False
            
        return True
