"""
Modelo de datos para Corredor
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Corredor:
    """
    Modelo de datos para representar un Corredor
    """
    id: str
    numero: int
    email: str
    nombre: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    activo: bool = True
    password: Optional[str] = None  # Solo se usa al crear/actualizar

    @classmethod
    def from_dict(cls, data: dict) -> 'Corredor':
        """
        Crea una instancia de Corredor desde un diccionario
        
        Args:
            data: Diccionario con los datos del corredor
            
        Returns:
            Corredor: Nueva instancia de Corredor
        """
        return cls(
            id=str(data.get('id')),
            numero=int(data.get('numero', 0)),
            email=data.get('email', ''),
            nombre=data.get('nombre', ''),
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            fecha_registro=datetime.fromisoformat(data['fecha_registro']) 
                if data.get('fecha_registro') else None,
            activo=data.get('activo', True),
            password=None  # No almacenamos la contraseña en el modelo
        )

    def to_dict(self, include_password: bool = False) -> dict:
        """
        Convierte la instancia a un diccionario
        
        Args:
            include_password: Si se debe incluir la contraseña en el diccionario
            
        Returns:
            dict: Diccionario con los datos del corredor
        """
        data = {
            'id': self.id,
            'numero': self.numero,
            'email': self.email,
            'nombre': self.nombre,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'fecha_registro': self.fecha_registro.isoformat() 
                if self.fecha_registro else None,
            'activo': self.activo
        }
        
        # Solo incluir contraseña si se solicita explícitamente y existe
        if include_password and self.password:
            data['password'] = self.password
            
        return data

    def actualizar(self, datos: dict) -> None:
        """
        Actualiza los datos del corredor
        
        Args:
            datos: Diccionario con los datos a actualizar
        """
        if 'numero' in datos:
            self.numero = int(datos['numero'])
        if 'email' in datos:
            self.email = datos['email']
        if 'nombre' in datos:
            self.nombre = datos['nombre']
        if 'telefono' in datos:
            self.telefono = datos['telefono']
        if 'direccion' in datos:
            self.direccion = datos['direccion']
        if 'activo' in datos:
            self.activo = datos['activo']
        if 'password' in datos:
            self.password = datos['password']
