"""
Clase base para todos los repositorios de la aplicación
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class RepositorioBase(Generic[T], ABC):
    """Interfaz base para repositorios"""

    @abstractmethod
    async def obtener_todos(self) -> List[T]:
        """Obtiene todos los elementos"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[T]:
        """Obtiene un elemento por su ID"""
        pass

    @abstractmethod
    async def crear(self, item: T) -> T:
        """Crea un nuevo elemento"""
        pass

    @abstractmethod
    async def actualizar(self, item: T) -> T:
        """Actualiza un elemento existente"""
        pass

    @abstractmethod
    async def eliminar(self, id: int) -> bool:
        """Elimina un elemento por su ID"""
        pass
