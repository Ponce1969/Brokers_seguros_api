from datetime import date
from typing import Optional, Any, Dict

from pydantic import BaseModel, EmailStr, Field, model_validator


class CorredorBase(BaseModel):
    nombres: Optional[str] = None
    apellidos: str
    documento: str
    direccion: str
    localidad: str
    telefonos: Optional[str] = None
    movil: Optional[str] = None
    mail: EmailStr
    observaciones: Optional[str] = None
    matricula: Optional[str] = None
    especializacion: Optional[str] = None


class CorredorCreate(CorredorBase):
    numero: int = Field(..., ge=1000, le=9999, description="Número de 4 cifras asignado por el admin")
    fecha_alta: Optional[date] = None


class CorredorUpdate(CorredorBase):
    fecha_baja: Optional[date] = None


class CorredorResponse(BaseModel):
    id: int
    numero: int
    email: str
    nombre: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_registro: Optional[date] = None
    activo: bool = True
    
    @model_validator(mode='before')
    @classmethod
    def map_fields(cls, data: Any) -> Dict[str, Any]:
        """
        Mapea los campos del modelo de la base de datos a los campos del schema
        cuando se usa from_attributes=True
        
        También maneja el caso de diccionarios que ya vienen de la API para crear/actualizar
        """
        # Si ya es un diccionario, verificamos si necesitamos mapear campos
        if isinstance(data, dict):
            result = data.copy()
            
            # Si estamos en un proceso POST donde data ya viene con campos correctos 
            # del modelo de datos pero necesitamos adaptarlos al response
            if 'mail' in result and 'email' not in result:
                result['email'] = result.pop('mail')
                
            if ('nombres' in result or 'apellidos' in result) and 'nombre' not in result:
                nombres = result.get('nombres', '')
                apellidos = result.get('apellidos', '')
                result['nombre'] = f"{nombres or ''} {apellidos or ''}".strip()
                
            if 'telefonos' in result and 'telefono' not in result:
                result['telefono'] = result.pop('telefonos')
                
            if 'fecha_alta' in result and 'fecha_registro' not in result:
                result['fecha_registro'] = result.get('fecha_alta')
                
            # Calcular si está activo
            result['activo'] = True if 'fecha_baja' not in result or result.get('fecha_baja') is None else False
            
            return result
        
        # Si es un objeto ORM (normalmente de una consulta GET)
        result = {}
        
        # Copiar ID y número
        if hasattr(data, 'id'):
            result['id'] = data.id
        if hasattr(data, 'numero'):
            result['numero'] = data.numero
            
        # Mapear mail a email
        if hasattr(data, 'mail'):
            result['email'] = data.mail
            
        # Componer nombre completo
        nombres = getattr(data, 'nombres', '')
        apellidos = getattr(data, 'apellidos', '')
        result['nombre'] = f"{nombres or ''} {apellidos or ''}".strip()
        
        # Mapear telefonos a telefono
        if hasattr(data, 'telefonos'):
            result['telefono'] = data.telefonos
            
        # Copiar direccion directamente
        if hasattr(data, 'direccion'):
            result['direccion'] = data.direccion
            
        # Fecha de registro y activo (suponemos true por defecto)
        result['fecha_registro'] = getattr(data, 'fecha_alta', None)
        result['activo'] = True if not hasattr(data, 'fecha_baja') or data.fecha_baja is None else False
        
        return result

    class Config:
        from_attributes = True


class Corredor(CorredorBase):
    numero: int = Field(..., ge=1000, le=9999, description="Número de 4 cifras asignado por el admin")
    fecha_alta: Optional[date] = None
    fecha_baja: Optional[date] = None

    class Config:
        from_attributes = True
