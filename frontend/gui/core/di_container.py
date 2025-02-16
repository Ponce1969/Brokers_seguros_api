"""
Contenedor de Inyección de Dependencias para la aplicación
"""

from typing import Dict, Type, Any
from dataclasses import dataclass, field


@dataclass
class ContenedorDI:
    """Contenedor para inyección de dependencias"""

    _instancias: Dict[Type, Any] = field(default_factory=dict)
    _fabricas: Dict[Type, Any] = field(default_factory=dict)

    def registrar_instancia(self, tipo_interfaz: Type, instancia: Any) -> None:
        """Registra una instancia para un tipo"""
        self._instancias[tipo_interfaz] = instancia

    def registrar_fabrica(self, tipo_interfaz: Type, fabrica) -> None:
        """Registra una función fábrica para un tipo"""
        self._fabricas[tipo_interfaz] = fabrica

    def resolver(self, tipo_interfaz: Type) -> Any:
        """Resuelve una instancia para un tipo"""
        if tipo_interfaz in self._instancias:
            return self._instancias[tipo_interfaz]

        if tipo_interfaz in self._fabricas:
            instancia = self._fabricas[tipo_interfaz]()
            self._instancias[tipo_interfaz] = instancia
            return instancia

        raise Exception(f"No se encontró registro para {tipo_interfaz}")


# Instancia global del contenedor
contenedor = ContenedorDI()
