"""
Modelo de datos para Corredor
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Union
from datetime import datetime, date
import logging
import re

# Configurar logging
logger = logging.getLogger(__name__)


@dataclass
class Corredor:
    """
    Modelo de datos para representar un Corredor
    """

    # Campos reflejando exactamente la estructura del backend
    id: int  # Clave primaria técnica (autoincremental)
    numero: int  # Identificador de negocio
    email: str  # Email del corredor (en backend: 'email')
    nombre: str  # Nombre completo (en backend: 'nombre')
    telefono: str  # Teléfono (en backend: 'telefono')
    direccion: str  # Dirección (en backend: 'direccion')
    documento: str  # Documento (en backend: 'documento')
    tipo: str = field(default="corredor")  # Tipo de corredor
    fecha_registro: Optional[date] = field(default=None)
    activo: bool = field(default=True)
    fecha_alta: Optional[date] = field(default=None)
    fecha_baja: Optional[date] = field(default=None)
    rol: str = field(default="corredor")  # "corredor" o "admin"
    password: Optional[str] = field(default=None)  # Para nuevos corredores
    
    # Mantenemos algunos campos opcionales para compatibilidad con la API
    fecha_baja: Optional[date] = field(default=None)
    
    # Propiedades para compatibilidad con expectativas del backend
    # Esto nos permite usar ambos nombres de campos (singular y plural)
    # sin cambiar todo el código existente
    
    @property
    def nombres(self) -> str:
        """Obtiene el primer nombre del nombre completo (para backend)"""
        partes = self.nombre.split(' ', 1)
        return partes[0] if partes else ""
        
    @property
    def apellidos(self) -> str:
        """Obtiene los apellidos del nombre completo (para backend)"""
        partes = self.nombre.split(' ', 1)
        return partes[1] if len(partes) > 1 else "Sin Apellido"
    
    @property
    def mail(self) -> str:
        """Alias para email (para backend)"""
        return self.email
        
    @property
    def telefonos(self) -> str:
        """Alias para telefono (para backend)"""
        return self.telefono
        
    @property
    def movil(self) -> str:
        """Alias para telefono como móvil (para backend)"""
        return self.telefono
        
    @property
    def localidad(self) -> str:
        """Localidad por defecto (requerido por backend)"""
        return "Montevideo"

    @classmethod
    def from_dict(cls, data: dict) -> "Corredor":
        """
        Crea una instancia de Corredor desde un diccionario

        Args:
            data: Diccionario con los datos del corredor

        Returns:
            Corredor: Nueva instancia de Corredor
        """
        try:
            # Validaciones básicas
            if "email" in data and data["email"] and not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
                raise ValueError(f"Email inválido: {data['email']}")
            
            if "telefono" in data and data["telefono"] and not re.match(r"^[\d\s\+\-\(\)]+$", data["telefono"]):
                raise ValueError(f"Formato de teléfono inválido: {data['telefono']}")
            
            # Procesar fechas
            fecha_registro = None
            if data.get("fecha_registro"):
                try:
                    fecha_registro = datetime.strptime(data["fecha_registro"], "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Error al procesar fecha_registro: {data['fecha_registro']}")
                    raise ValueError(f"Formato de fecha_registro inválido: {data['fecha_registro']}")

            fecha_alta = None
            if data.get("fecha_alta"):
                try:
                    fecha_alta = datetime.strptime(data["fecha_alta"], "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Error al procesar fecha_alta: {data['fecha_alta']}")
                    raise ValueError(f"Formato de fecha_alta inválido: {data['fecha_alta']}")



            fecha_baja = None
            if data.get("fecha_baja"):
                try:
                    fecha_baja = datetime.strptime(data["fecha_baja"], "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Error al procesar fecha_baja: {data['fecha_baja']}")
                    raise ValueError(f"Formato de fecha_baja inválido: {data['fecha_baja']}")
                    
            # Validación de fechas coherentes
            if fecha_alta and fecha_baja and fecha_alta > fecha_baja:
                raise ValueError("La fecha de alta no puede ser posterior a la fecha de baja")

            # Crear instancia de corredor con campos que coincidan con el backend
            return cls(
                id=int(data.get("id", 0)),
                numero=int(data.get("numero", 0)),
                email=data.get("email", ""),
                nombre=data.get("nombre", ""),
                telefono=data.get("telefono", ""),
                direccion=data.get("direccion", ""),
                documento=data.get("documento", ""),
                tipo=data.get("tipo", "corredor"),
                fecha_registro=fecha_registro,
                activo=data.get("activo", True),
                fecha_alta=fecha_alta,
                fecha_baja=fecha_baja,
                rol=data.get("rol", "corredor"),
                password=data.get("password")
            )
        except Exception as e:
            logger.error(f"Error al crear Corredor desde diccionario: {e}")
            logger.error(f"Datos recibidos: {data}")
            raise

    def to_dict(self) -> dict:
        """
        Convierte la instancia a un diccionario

        Returns:
            dict: Diccionario con los datos del corredor en formato compatible con el backend
        """
        # Convertir fechas a string si existen
        fecha_registro_str = None
        if self.fecha_registro:
            fecha_registro_str = self.fecha_registro.strftime("%Y-%m-%d")
            
        fecha_alta_str = None
        if self.fecha_alta:
            fecha_alta_str = self.fecha_alta.strftime("%Y-%m-%d")
            
        fecha_baja_str = None
        if self.fecha_baja:
            fecha_baja_str = self.fecha_baja.strftime("%Y-%m-%d")
            
        data = {
            "id": self.id,
            "numero": self.numero,
            "email": self.email,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "documento": self.documento,  # Incluir campo documento
            "fecha_registro": fecha_registro_str,
            "activo": self.activo,
            "rol": self.rol,
            "fecha_alta": fecha_alta_str,
            "fecha_baja": fecha_baja_str,
        }
        
        # Solo incluir password si existe y no enviarlo en respuestas de API
        if hasattr(self, 'password') and self.password:
            data["password"] = "[PROTEGIDO]"  # No mostramos la contraseña real en la interfaz
        return {k: v for k, v in data.items() if v is not None}
    
    def _parse_fecha(self, valor: str) -> Optional[date]:
        """
        Parsea una cadena de texto a un objeto date.
        
        Args:
            valor: Cadena de texto en formato 'YYYY-MM-DD'
            
        Returns:
            date: Objeto date o None si hubo un error
            
        Raises:
            ValueError: Si el formato de la fecha es inválido
        """
        if not valor:
            return None
            
        try:
            return datetime.strptime(valor, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Error al convertir fecha: {valor}")
            raise ValueError(f"Formato de fecha inválido: {valor}")

    def actualizar(self, datos: dict) -> None:
        """
        Actualiza los datos del corredor con validación de tipos.

        Args:
            datos: Diccionario con los datos a actualizar
        """
        for campo, valor in datos.items():
            if hasattr(self, campo):
                try:
                    # Manejar campos específicos por tipo
                    if campo in ["fecha_registro", "fecha_alta", "fecha_baja"]:
                        if valor is not None:
                            valor = self._parse_fecha(valor) if isinstance(valor, str) else valor
                            
                    elif campo in ["id", "numero"]:
                        if valor is not None and not isinstance(valor, int):
                            try:
                                valor = int(valor)
                            except (ValueError, TypeError):
                                logger.warning(f"Se esperaba un int para {campo}, pero se recibió {type(valor)}")
                                continue
                                
                    elif campo == "activo" and not isinstance(valor, bool):
                        if isinstance(valor, str):
                            valor = valor.lower() in ("true", "t", "1", "yes", "y")
                        elif isinstance(valor, int):
                            valor = bool(valor)
                        else:
                            logger.warning(f"Se esperaba un bool para {campo}, pero se recibió {type(valor)}")
                            continue
                            
                    # Validar formato de campos de texto específicos
                    elif campo == "email" and valor and not re.match(r"[^@]+@[^@]+\.[^@]+", valor):
                        raise ValueError(f"Email inválido: {valor}")
                        
                    elif campo == "telefono" and valor and not re.match(r"^[\d\s\+\-\(\)]+$", valor):
                        raise ValueError(f"Formato de teléfono inválido: {valor}")
                        
                    # Asignar el valor
                    setattr(self, campo, valor)
                    
                except Exception as e:
                    logger.error(f"Error al actualizar campo '{campo}': {e}")
                    raise
                    
        # Verificar coherencia de fechas después de actualizar
        if self.fecha_alta and self.fecha_baja and self.fecha_alta > self.fecha_baja:
            raise ValueError("La fecha de alta no puede ser posterior a la fecha de baja")
